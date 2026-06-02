from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any


_SCHEMA_VERSION = 3

# Freshness thresholds by retention tier.
_SHORT_TERM_FRESH_HOURS: float = 1.0   # short_term: fresh if updated < 1 h ago
_SHORT_TERM_STALE_HOURS: float = 4.0   # short_term: stale if not updated for > 4 h
# long_term facts are always fresh and never stale.


def _age_metadata(updated_at: str, retention: str = "long_term") -> dict:
    """Compute age-hours and freshness flags from an ISO-8601 UTC timestamp.

    Thresholds vary by retention tier:
    - ``long_term``: always fresh, never stale (assumed to remain valid indefinitely).
    - ``short_term``: fresh < 1 h; stale > 4 h (warns before the 8 h auto-TTL expires).
    """
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0
    except (ValueError, TypeError):
        age_h = 0.0
    if retention == "long_term":
        is_fresh, is_stale = True, False
    else:  # short_term
        is_fresh = age_h < _SHORT_TERM_FRESH_HOURS
        is_stale = age_h > _SHORT_TERM_STALE_HOURS
    return {
        "age_hours": round(age_h, 2),
        "is_fresh": is_fresh,
        "is_stale": is_stale,
    }


def _tokenize_hint(text: str) -> frozenset[str]:
    """Split a task-hint string into lowercase alphanumeric tokens."""
    return frozenset(re.findall(r"[a-z0-9]+", text.lower())) if text else frozenset()


def _score_task_relevance(fact: dict, hint_tokens: frozenset[str]) -> int:
    """Count how many hint tokens appear in the fact's key, source_description, or value."""
    if not hint_tokens:
        return 0
    haystack = " ".join(filter(None, [
        fact.get("key", ""),
        fact.get("source_description") or "",
        (fact.get("value") or "")[:200],
    ])).lower()
    return len(hint_tokens & frozenset(re.findall(r"[a-z0-9]+", haystack)))


def get_conn(root: str) -> sqlite3.Connection:
    path = Path(root) / ".github" / "xanadAssistant" / "memory" / "memory.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    init_db(conn)
    return conn


def chk_scope(value: str, valid_scopes: set[str]) -> None:
    if value not in valid_scopes:
        raise ValueError(f"scope must be one of {sorted(valid_scopes)}; got {value!r}")


def chk_rule_type(value: str, valid_rule_types: set[str]) -> None:
    if value not in valid_rule_types:
        raise ValueError(f"rule_type must be one of {sorted(valid_rule_types)}; got {value!r}")


def chk_agent(value: str | None, agent_re) -> None:
    if value is not None and not agent_re.match(value):
        raise ValueError(f"agent must be alphanumeric+hyphens; got {value!r}")


def chk_branch(value: str | None, branch_re) -> None:
    if value is not None and not branch_re.match(value):
        raise ValueError(f"branch must be alphanumeric with ._/-; got {value!r}")


def chk_confidence(value: float) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"confidence must be numeric; got {value!r}") from exc
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be between 0.0 and 1.0; got {value!r}")
    return confidence


def init_db(conn: sqlite3.Connection) -> None:
    is_fresh = not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='advisory_memory'"
    ).fetchone()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS advisory_memory (
            agent TEXT NOT NULL, scope TEXT NOT NULL, branch TEXT NOT NULL DEFAULT '',
            session_id TEXT NOT NULL DEFAULT '', key TEXT NOT NULL, value TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            source TEXT NOT NULL DEFAULT 'agent-discovered',
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            expires_at TEXT, valid_from TEXT, valid_until TEXT, invalidated_at TEXT,
            source_description TEXT,
            retention TEXT NOT NULL DEFAULT 'long_term',
            UNIQUE (agent, scope, branch, session_id, key)
        );
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT, scope TEXT NOT NULL DEFAULT 'workspace', branch TEXT,
            rule_type TEXT NOT NULL, description TEXT NOT NULL,
            created_by TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        );
        CREATE TABLE IF NOT EXISTS agent_diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'workspace',
            branch TEXT NOT NULL DEFAULT '', session_id TEXT NOT NULL DEFAULT '',
            entry TEXT NOT NULL, tags TEXT NOT NULL DEFAULT '',
            recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS agent_diary_fts
            USING fts5(id UNINDEXED, agent UNINDEXED, scope UNINDEXED,
                       branch UNINDEXED, session_id UNINDEXED, entry, tags);
    """)
    if is_fresh:
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
    conn.commit()
    _run_schema_migrations(conn)
    migrate_fts_if_needed(conn)


def _add_column_safe(conn: sqlite3.Connection, table: str, col: str, typedef: str) -> None:
    """Add a column if it does not already exist (idempotent).

    Only swallows ``OperationalError`` on a concurrent-add race (the column
    appears in a re-check).  Any other failure is re-raised so schema
    migrations cannot silently mark themselves complete after a real error.
    """
    if col not in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            if col not in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}:
                raise  # column still missing — not a race; propagate the real error


def _rebuild_advisory_memory(conn: sqlite3.Connection) -> None:
    """Rebuild advisory_memory with the correct 5-column UNIQUE constraint."""
    conn.execute("""CREATE TABLE advisory_memory_v2 (
        agent TEXT NOT NULL, scope TEXT NOT NULL, branch TEXT NOT NULL DEFAULT '',
        session_id TEXT NOT NULL DEFAULT '', key TEXT NOT NULL, value TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 1.0, source TEXT NOT NULL DEFAULT 'agent-discovered',
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
        expires_at TEXT, valid_from TEXT, valid_until TEXT, invalidated_at TEXT,
        source_description TEXT, UNIQUE (agent, scope, branch, session_id, key))""")
    conn.execute("""INSERT OR IGNORE INTO advisory_memory_v2
        (agent, scope, branch, session_id, key, value, confidence, source,
         updated_at, expires_at, valid_from, valid_until, invalidated_at, source_description)
        SELECT agent, scope, branch, COALESCE(session_id, ''), key, value, confidence, source,
               updated_at, expires_at, valid_from, valid_until, invalidated_at, source_description
        FROM advisory_memory""")
    conn.execute("DROP TABLE advisory_memory")
    conn.execute("ALTER TABLE advisory_memory_v2 RENAME TO advisory_memory")


def _run_schema_migrations(conn: sqlite3.Connection) -> None:
    """Upgrade the schema to _SCHEMA_VERSION using PRAGMA user_version for safe versioning."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= _SCHEMA_VERSION:
        return
    # v0 → v1: add session_id and source_description to advisory_memory.
    if version < 1:
        _add_column_safe(conn, "advisory_memory", "session_id", "TEXT NOT NULL DEFAULT ''")
        _add_column_safe(conn, "advisory_memory", "source_description", "TEXT")
    # v1 → v2: rebuild advisory_memory with new UNIQUE key; add session_id to agent_diary.
    if version < 2:
        _rebuild_advisory_memory(conn)
        _add_column_safe(conn, "agent_diary", "session_id", "TEXT NOT NULL DEFAULT ''")
    # v2 → v3: add retention tier to advisory_memory.
    if version < 3:
        _add_column_safe(conn, "advisory_memory", "retention", "TEXT NOT NULL DEFAULT 'long_term'")
    conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
    conn.commit()


def migrate_fts_if_needed(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_diary_fts'"
    ).fetchone()
    if row and row[0] and "agent UNINDEXED" in row[0] and "session_id UNINDEXED" in row[0]:
        return
    conn.execute("DROP TABLE IF EXISTS agent_diary_fts")
    conn.execute(
        "CREATE VIRTUAL TABLE agent_diary_fts "
        "USING fts5(id UNINDEXED, agent UNINDEXED, scope UNINDEXED, "
        "branch UNINDEXED, session_id UNINDEXED, entry, tags)"
    )
    conn.execute(
        "INSERT INTO agent_diary_fts (id,agent,scope,branch,session_id,entry,tags) "
        "SELECT id,agent,scope,branch,COALESCE(session_id,''),entry,tags FROM agent_diary"
    )
    conn.commit()


def rows(rows_in: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(zip(row.keys(), tuple(row))) for row in rows_in]


def row(row_in: sqlite3.Row) -> dict[str, Any]:
    return dict(zip(row_in.keys(), tuple(row_in)))


def render_rows(rows_in: list[sqlite3.Row], empty_message: str, render_row) -> str:
    if not rows_in:
        return empty_message
    return "\n".join(render_row(row_in) for row_in in rows_in)


def prune_extra(agent: str | None, scope: str | None) -> tuple[str, list[Any]]:
    where = ""
    params: list[Any] = []
    if agent:
        where += " AND agent=?"
        params.append(agent)
    if scope:
        where += " AND scope=?"
        params.append(scope)
    return where, params


def active_fact_where() -> str:
    return (
        "  AND invalidated_at IS NULL "
        "  AND (expires_at IS NULL OR expires_at > strftime('%Y-%m-%dT%H:%M:%SZ','now')) "
        "  AND (valid_from IS NULL OR valid_from <= strftime('%Y-%m-%dT%H:%M:%SZ','now')) "
        "  AND (valid_until IS NULL OR valid_until > strftime('%Y-%m-%dT%H:%M:%SZ','now'))"
    )


_SCOPE_RANK: dict[str, int] = {"session": 0, "branch": 1, "project": 2, "workspace": 3}


def _collapse_facts_by_key(facts: list[dict], primary_agent: str) -> list[dict]:
    """For each unique key, keep one fact: primary agent wins over shared; higher scope wins."""
    best: dict[str, dict] = {}
    for fact in facts:
        key = fact["key"]
        if key not in best:
            best[key] = fact
            continue
        challenger, champion = fact, best[key]
        c_primary = challenger["agent"] == primary_agent
        ch_primary = champion["agent"] == primary_agent
        if c_primary and not ch_primary:
            best[key] = challenger
        elif not c_primary and ch_primary:
            pass  # champion wins
        elif _SCOPE_RANK.get(challenger["scope"], 99) < _SCOPE_RANK.get(champion["scope"], 99):
            best[key] = challenger
    result: list[dict] = []
    seen: set[str] = set()
    for f in facts:
        k = f["key"]
        if k not in seen and best.get(k) is f:
            result.append(f)
            seen.add(k)
    return result


def memory_dump(agent: str, root: str, branch: str, session_id: str = "", task_hint: str = "") -> str:
    """Return currently applicable rules and facts as JSON, enriched with age metadata.

    When *task_hint* is provided, each fact gains a ``relevance_score`` (token-overlap
    with the hint) and facts are sorted by score descending before being returned.
    The top-level ``summary`` key lets callers skip memory-dependent steps quickly
    when ``has_data`` is ``false``.
    """
    with closing(get_conn(root)) as conn:
        rules = rows(
            conn.execute(
                "SELECT id, rule_type, description, scope, branch, created_at FROM rules "
                "WHERE (agent IS NULL OR agent=?) "
                "  AND (branch IS NULL OR branch='' OR branch=?) "
                "  AND scope != 'session' "
                "ORDER BY created_at",
                (agent, branch),
            ).fetchall()
        )
        raw_facts = rows(
            conn.execute(
                """
                SELECT agent, scope, branch, key, value, confidence, source,
                       updated_at, expires_at, valid_from, valid_until, source_description,
                       retention
                FROM advisory_memory
                WHERE agent IN (?, ?) AND branch IN (?, ?)
                                AND (scope != 'session' OR session_id = ?)
                                AND invalidated_at IS NULL
                                AND (expires_at IS NULL OR expires_at > strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                                AND (valid_from IS NULL OR valid_from <= strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                                AND (valid_until IS NULL OR valid_until > strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                ORDER BY
                    CASE WHEN agent=? THEN 0 ELSE 1 END,
                    CASE WHEN updated_at >= strftime('%Y-%m-%dT%H:%M:%SZ',
                         datetime('now', '-1 day')) THEN 0 ELSE 1 END,
                    confidence DESC
                """,
                (agent, "shared", "", branch, session_id, agent),
            ).fetchall()
        )
    hint_tokens = _tokenize_hint(task_hint)
    collapsed = _collapse_facts_by_key(raw_facts, agent)
    enriched: list[dict] = []
    fresh_count = stale_count = short_term_count = long_term_count = 0
    for fact in collapsed:
        ret = fact.get("retention", "long_term")
        meta = _age_metadata(fact["updated_at"], ret)
        ef = {**fact, **meta}
        if hint_tokens:
            ef["relevance_score"] = _score_task_relevance(fact, hint_tokens)
        if meta["is_fresh"]:
            fresh_count += 1
        if meta["is_stale"]:
            stale_count += 1
        if ret == "short_term":
            short_term_count += 1
        else:
            long_term_count += 1
        enriched.append(ef)
    if hint_tokens:
        enriched.sort(key=lambda f: f.get("relevance_score", 0), reverse=True)
    summary = {
        "total_rules": len(rules),
        "total_facts": len(enriched),
        "has_data": bool(rules or enriched),
        "fresh_count": fresh_count,
        "stale_count": stale_count,
        "short_term_count": short_term_count,
        "long_term_count": long_term_count,
    }
    return json.dumps({"summary": summary, "rules": rules, "facts": enriched})


def memory_prune(agent: str | None, scope: str | None, max_age_days: float | None, root: str) -> str:
    if max_age_days is not None and max_age_days <= 0:
        raise ValueError(
            f"max_age_days must be > 0; got {max_age_days!r}. "
            "Pass None to only remove expired rows."
        )
    extra, extra_params = prune_extra(agent, scope)
    with closing(get_conn(root)) as conn:
        expired = conn.execute(
            "DELETE FROM advisory_memory WHERE expires_at IS NOT NULL "
            f"AND expires_at <= strftime('%Y-%m-%dT%H:%M:%SZ','now'){extra}",
            extra_params,
        )
        expired_deleted = expired.rowcount
        age_deleted = 0
        diary_deleted = 0
        if max_age_days is not None:
            cutoff_secs = int(float(max_age_days) * 86400)
            offset = f"-{cutoff_secs} seconds"
            stale = conn.execute(
                f"DELETE FROM advisory_memory WHERE updated_at <= "
                f"strftime('%Y-%m-%dT%H:%M:%SZ',datetime('now',?)){extra}",
                [offset, *extra_params],
            )
            age_deleted = stale.rowcount
            old_ids = [
                row_in[0]
                for row_in in conn.execute(
                    f"SELECT id FROM agent_diary WHERE recorded_at <= "
                    f"strftime('%Y-%m-%dT%H:%M:%SZ',datetime('now',?)){extra}",
                    [offset, *extra_params],
                ).fetchall()
            ]
            if old_ids:
                placeholders = ",".join("?" * len(old_ids))
                conn.execute(f"DELETE FROM agent_diary WHERE id IN ({placeholders})", old_ids)
                conn.execute(f"DELETE FROM agent_diary_fts WHERE id IN ({placeholders})", old_ids)
                diary_deleted = len(old_ids)
        conn.commit()
    return (
        f"Pruned {expired_deleted} expired + {age_deleted} stale advisory_memory rows; "
        f"{diary_deleted} diary rows."
    )


def rule_add(description: str, rule_type: str, agent: str | None, scope: str, branch: str | None, root: str) -> str:
    if scope == "session":
        raise ValueError(
            "scope='session' is not supported for rules; rule session-isolation is not yet "
            "implemented. Use scope='workspace' for persistent rules."
        )
    if branch and scope != "branch":
        raise ValueError(
            f"branch must be None or empty for scope={scope!r}; "
            "use scope='branch' for branch-scoped rules."
        )
    with closing(get_conn(root)) as conn:
        cur = conn.execute(
            "INSERT INTO rules (agent,scope,branch,rule_type,description) VALUES (?,?,?,?,?)",
            (agent, scope, branch, rule_type, description),
        )
        conn.commit()
        rule_id = cur.lastrowid
    return f"Rule #{rule_id} added [{rule_type}]: {description}"


def rule_list(agent: str | None, scope: str, branch: str, root: str) -> str:
    branch_clause = "AND (branch IS NULL OR branch=?) " if scope == "branch" else ""
    branch_params: list = [branch] if scope == "branch" else []
    with closing(get_conn(root)) as conn:
        rows_in = conn.execute(
            "SELECT id, rule_type, agent, description, created_at FROM rules "
            "WHERE scope=? AND (agent IS NULL OR agent=?) "
            + branch_clause
            + "ORDER BY created_at",
            (scope, agent, *branch_params),
        ).fetchall()
    return render_rows(
        rows_in,
        f"No rules for scope {scope!r}.",
        lambda row_in: f"[#{row_in['id']} {row_in['rule_type']}] {row_in['description']}  (agent={row_in['agent'] or '*'})",
    )


def rule_remove(rule_id: int, root: str) -> str:
    with closing(get_conn(root)) as conn:
        cur = conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))
        conn.commit()
        deleted = cur.rowcount
    return f"Rule #{rule_id} deleted." if deleted else f"No rule with id {rule_id}."


def diary_add(agent: str, entry: str, scope: str, tags: str, branch: str, session_id: str, root: str) -> str:
    with closing(get_conn(root)) as conn:
        with conn:
            cur = conn.execute(
                "INSERT INTO agent_diary (agent,scope,branch,session_id,entry,tags) VALUES (?,?,?,?,?,?)",
                (agent, scope, branch, session_id, entry, tags),
            )
            diary_id = cur.lastrowid
            conn.execute(
                "INSERT INTO agent_diary_fts (id,agent,scope,branch,session_id,entry,tags) VALUES (?,?,?,?,?,?,?)",
                (diary_id, agent, scope, branch, session_id, entry, tags),
            )
    return f"Diary entry #{diary_id} recorded for {agent!r}."


def diary_get(agent: str, scope: str, limit: int, tag: str | None, branch: str, session_id: str, root: str) -> str:
    branch_clause = "AND branch=? " if scope == "branch" else ""
    branch_params: list[str] = [branch] if scope == "branch" else []
    session_clause = "AND session_id=? " if scope == "session" else ""
    session_params: list[str] = [session_id] if scope == "session" else []
    with closing(get_conn(root)) as conn:
        if tag:
            rows_in = conn.execute(
                "SELECT id, entry, tags, recorded_at FROM agent_diary "
                "WHERE agent=? AND scope=? "
                + branch_clause + session_clause
                + "  AND (',' || tags || ',' LIKE '%,' || ? || ',%') "
                "ORDER BY recorded_at DESC, id DESC LIMIT ?",
                (agent, scope, *branch_params, *session_params, tag, limit),
            ).fetchall()
        else:
            rows_in = conn.execute(
                "SELECT id, entry, tags, recorded_at FROM agent_diary "
                "WHERE agent=? AND scope=? "
                + branch_clause + session_clause
                + "ORDER BY recorded_at DESC, id DESC LIMIT ?",
                (agent, scope, *branch_params, *session_params, limit),
            ).fetchall()
    return render_rows(
        rows_in,
        f"No diary entries for {agent!r} in scope {scope!r}.",
        lambda row_in: f"[#{row_in['id']} {row_in['recorded_at']}] {row_in['entry']}  tags={row_in['tags']}",
    )


def diary_search(agent: str, query: str, scope: str, limit: int, include_agents: list[str] | None, branch: str, session_id: str, root: str) -> str:
    # Wrap in FTS5 double-quoted phrase to neutralise special characters (-, :, OR, NOT, etc.).
    safe_query = '"' + query.replace('"', '""') + '"'
    agents = [agent]
    for extra_agent in include_agents or []:
        if extra_agent not in agents:
            agents.append(extra_agent)
    placeholders = ",".join("?" * len(agents))
    branch_clause = "AND branch=? " if scope == "branch" else ""
    branch_params: list[str] = [branch] if scope == "branch" else []
    session_clause = "AND session_id=? " if scope == "session" else ""
    session_params: list[str] = [session_id] if scope == "session" else []
    with closing(get_conn(root)) as conn:
        try:
            rows_in = conn.execute(
                f"SELECT d.id, d.agent, d.entry, d.tags, d.recorded_at "
                f"FROM agent_diary d "
                f"WHERE d.id IN ("
                f"  SELECT id FROM agent_diary_fts "
                f"  WHERE agent_diary_fts MATCH ? AND agent IN ({placeholders}) AND scope=? "
                + branch_clause + session_clause
                + f") "
                f"ORDER BY d.recorded_at DESC, d.id DESC LIMIT ?",
                (safe_query, *agents, scope, *branch_params, *session_params, limit),
            ).fetchall()
        except sqlite3.OperationalError as exc:
            raise RuntimeError(f"FTS5 search error: {exc}") from exc
    return render_rows(
        rows_in,
        f"No diary entries matched {query!r} for {agent!r}.",
        lambda row_in: f"[#{row_in['id']} {row_in['recorded_at']} {row_in['agent']}] {row_in['entry']}  tags={row_in['tags']}",
    )
