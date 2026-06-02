#!/usr/bin/env python3
"""SQLite-backed scoped memory MCP for facts, rules, and diary entries."""
from __future__ import annotations

from contextlib import closing
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as _exc:  # pragma: no cover
    sys.stderr.write(
        "ERROR: the 'mcp' package is required.\n"
        "Install with: pip install 'mcp[cli]'\n"
        f"Details: {_exc}\n"
    )
    sys.exit(1)

mcp = FastMCP("xanadMemory")
_VALID_SCOPES = {"workspace", "project", "branch", "session"}
_VALID_RULE_TYPES = {"never", "always", "prefer", "avoid"}
_VALID_RETENTIONS = {"short_term", "long_term"}
_VALID_RULE_SCOPES: frozenset[str] = frozenset({"workspace", "project", "branch"})
_SHORT_TERM_AUTO_TTL_DAYS: float = 8 / 24   # short_term facts auto-expire in 8 hours
_MAX_STR_LENS: dict[str, int] = {
    "key": 256,
    "value": 4096,
    "source_description": 1024,
    "description": 2048,
    "entry": 8192,
    "tags": 1024,
}
_AGENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]*$")
_SESSION_ID: str = str(uuid.uuid4())

from _memory_mcp_shared import (
    active_fact_where as _active_fact_where,
    chk_agent as _shared_chk_agent,
    chk_branch as _shared_chk_branch,
    chk_confidence as _shared_chk_confidence,
    chk_rule_type as _shared_chk_rule_type,
    chk_scope as _shared_chk_scope,
    diary_add as _shared_diary_add,
    diary_get as _shared_diary_get,
    diary_search as _shared_diary_search,
    get_conn as _get_conn,
    memory_dump as _shared_memory_dump,
    memory_prune as _shared_memory_prune,
    render_rows as _render_rows,
    row as _row,
    rule_add as _shared_rule_add,
    rule_list as _shared_rule_list,
    rule_remove as _shared_rule_remove,
)

def _workspace_root() -> str:
    v = os.environ.get("WORKSPACE_ROOT")
    if not v:
        raise ValueError("WORKSPACE_ROOT environment variable is not set.")
    return str(Path(v).resolve())


def _current_branch(root: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            b = r.stdout.strip()
            if b:
                return b
    except Exception:
        pass
    return None


def _advisory_branch(scope: str, root: str) -> str:
    if scope != "branch":
        return ""
    branch = _current_branch(root)
    if branch is None:
        raise ValueError(
            "Cannot resolve current git branch; branch-scoped memory operations are unavailable."
        )
    return branch


def _chk_rule_type(v: str) -> None:
    _shared_chk_rule_type(v, _VALID_RULE_TYPES)


def _chk_scope(v: str) -> None:
    _shared_chk_scope(v, _VALID_SCOPES)


def _chk_agent(v: str | None) -> None:
    _shared_chk_agent(v, _AGENT_RE)


_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/\-]{1,256}$")


def _chk_branch(v: str | None) -> None:
    _shared_chk_branch(v, _BRANCH_RE)


def _chk_confidence(v: float) -> float:
    return _shared_chk_confidence(v)


def _chk_retention(v: str) -> None:
    if v not in _VALID_RETENTIONS:
        raise ValueError(f"retention must be one of {sorted(_VALID_RETENTIONS)}; got {v!r}")


def _chk_rule_scope(v: str) -> None:
    """Validate scope for rule tools — session scope is not supported for rules."""
    _shared_chk_scope(v, _VALID_RULE_SCOPES)


def _chk_str_len(field: str, value: str | None) -> None:
    """Raise ValueError if value exceeds the registered per-field max length."""
    if value is not None and len(value) > _MAX_STR_LENS[field]:
        raise ValueError(
            f"{field!r} exceeds max length {_MAX_STR_LENS[field]}; got {len(value)} chars."
        )


def _parse_iso8601(value: str, field: str) -> str:
    """Parse and normalise an ISO-8601 timestamp to canonical ``YYYY-MM-DDTHH:MM:SSZ``."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    raise ValueError(f"{field!r} must be ISO-8601 UTC (e.g. '2026-01-15T00:00:00Z'); got {value!r}")


@mcp.tool()
def memory_set(
    agent: str, key: str, value: str,
    scope: str = "workspace", confidence: float = 1.0,
    source: str = "agent-discovered",
    ttl_days: float | None = None,
    valid_from: str | None = None, valid_until: str | None = None,
    source_description: str | None = None,
    retention: str = "long_term",
) -> str:
    """Upsert a fact into advisory memory.
    Args:
        agent: Agent identifier (alphanumeric + hyphens).
        key: Fact key (e.g. 'ci.commands', 'repo.language').
        value: Fact value as a string.
        scope: One of workspace/project/branch/session.
        confidence: 0.0–1.0 (1.0 = fully confident).
        source: Origin tag (default 'agent-discovered').
        ttl_days: If set, fact expires after this many days.
        valid_from: ISO-8601 UTC; fact not applicable before this date.
        valid_until: ISO-8601 UTC; soft validity end.
        retention: One of short_term/long_term. short_term auto-expires in 8 h.
    """
    _chk_agent(agent)
    _chk_scope(scope)
    _chk_retention(retention)
    _chk_str_len("key", key)
    _chk_str_len("value", value)
    _chk_str_len("source_description", source_description)
    if ttl_days is not None and ttl_days <= 0:
        raise ValueError(f"ttl_days must be > 0; got {ttl_days!r}. Pass None for no expiry.")
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    confidence = _chk_confidence(confidence)
    if valid_from is not None: valid_from = _parse_iso8601(valid_from, "valid_from")
    if valid_until is not None: valid_until = _parse_iso8601(valid_until, "valid_until")
    session_id = _SESSION_ID if scope == "session" else ""
    if retention == "short_term" and ttl_days is None:
        ttl_days = _SHORT_TERM_AUTO_TTL_DAYS
    expires_at: str | None = None
    if ttl_days is not None:
        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=ttl_days)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    with closing(_get_conn(root)) as conn:
        conn.execute(
            """
            INSERT INTO advisory_memory
                (agent, scope, branch, key, value, confidence, source,
                 expires_at, valid_from, valid_until, invalidated_at,
                 session_id, source_description, retention)
            VALUES (?,?,?,?,?,?,?,?,?,?,NULL,?,?,?)
            ON CONFLICT(agent,scope,branch,session_id,key) DO UPDATE SET
                value=excluded.value, confidence=excluded.confidence,
                source=excluded.source,
                updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'),
                expires_at=excluded.expires_at, valid_from=excluded.valid_from,
                valid_until=excluded.valid_until, invalidated_at=NULL,
                session_id=excluded.session_id,
                source_description=excluded.source_description,
                retention=excluded.retention
            """,
            (agent, scope, branch, key, value, confidence, source,
             expires_at, valid_from, valid_until, session_id, source_description, retention),
        )
        conn.commit()
    return f"Stored {key!r} for {agent!r} (scope={scope!r}, branch={branch!r})."


@mcp.tool()
def memory_get(
    agent: str, key: str, scope: str = "workspace",
    include_agents: list[str] | None = None,
) -> str:
    """Retrieve one currently applicable fact.

    Falls back to agent='shared'; cross-agent peek via include_agents.

    Args:
        agent: Primary agent identifier.
        key: Fact key to look up.
        scope: Scope to search within.
        include_agents: Additional agents to search (explicit opt-in).
    """
    _chk_agent(agent)
    _chk_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    agents = [agent]
    for a in (include_agents or []):
        _chk_agent(a)
        if a not in agents:
            agents.append(a)
    if "shared" not in agents:
        agents.append("shared")
    session_id_val = _SESSION_ID if scope == "session" else ""
    with closing(_get_conn(root)) as conn:
        for a in agents:
            row = conn.execute(
                "SELECT * FROM advisory_memory "
                "WHERE agent=? AND scope=? AND branch=? AND key=? AND session_id=? "
                + _active_fact_where(),
                (a, scope, branch, key, session_id_val),
            ).fetchone()
            if row:
                return json.dumps(_row(row))
    return f"No active fact for {key!r} (agent={agent!r}, scope={scope!r})."


@mcp.tool()
def memory_list(
    agent: str, scope: str = "workspace",
    include_shared: bool = True, include_agents: list[str] | None = None,
) -> str:
    """List all currently applicable fact keys for agent/scope.

    Cross-agent union via include_agents.

    Args:
        agent: Agent identifier.
        scope: Scope to list.
        include_shared: Also include agent='shared' keys.
        include_agents: Additional agents to union (explicit opt-in; same semantics as memory_get).
    """
    _chk_agent(agent)
    _chk_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    agents = [agent]
    if include_shared and "shared" not in agents:
        agents.append("shared")
    for a in (include_agents or []):
        _chk_agent(a)
        if a not in agents:
            agents.append(a)
    ph = ",".join("?" * len(agents))
    session_id_val = _SESSION_ID if scope == "session" else ""
    with closing(_get_conn(root)) as conn:
        rows = conn.execute(
            f"SELECT agent, key, confidence, updated_at FROM advisory_memory "
            f"WHERE agent IN ({ph}) AND scope=? AND branch=? AND session_id=? "
            f"{_active_fact_where()} "
            f"ORDER BY agent, key",
            (*agents, scope, branch, session_id_val),
        ).fetchall()
    return _render_rows(
        rows,
        f"No active facts for {agent!r} in scope {scope!r}.",
        lambda row: f"{row['agent']}/{row['key']}  conf={row['confidence']}  updated={row['updated_at']}",
    )


@mcp.tool()
def memory_remove(agent: str, key: str, scope: str = "workspace") -> str:
    """Hard-delete one advisory memory entry.

    Args:
        agent: Agent identifier.
        key: Fact key to delete.
        scope: Scope of the fact.
    """
    _chk_agent(agent)
    _chk_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    session_id_val = _SESSION_ID if scope == "session" else ""
    with closing(_get_conn(root)) as conn:
        cur = conn.execute(
            "DELETE FROM advisory_memory WHERE agent=? AND scope=? AND branch=? AND key=? AND session_id=?",
            (agent, scope, branch, key, session_id_val),
        )
        conn.commit()
        deleted = cur.rowcount
    return f"Removed {key!r}." if deleted else f"No entry for {key!r}."


@mcp.tool()
def memory_invalidate(agent: str, key: str, scope: str = "workspace") -> str:
    """Soft-delete a fact: sets invalidated_at; row kept for audit.

    Args:
        agent: Agent identifier.
        key: Fact key to invalidate.
        scope: Scope of the fact.
    """
    _chk_agent(agent)
    _chk_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    session_id_val = _SESSION_ID if scope == "session" else ""
    with closing(_get_conn(root)) as conn:
        cur = conn.execute(
            "UPDATE advisory_memory "
            "SET invalidated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') "
            "WHERE agent=? AND scope=? AND branch=? AND key=? AND session_id=? AND invalidated_at IS NULL",
            (agent, scope, branch, key, session_id_val),
        )
        conn.commit()
        updated = cur.rowcount
    return (
        f"Invalidated {key!r} (row kept for audit)." if updated
        else f"No active entry for {key!r}."
    )


@mcp.tool()
def memory_dump(agent: str, task_hint: str = "") -> str:
    """Return currently applicable rules and facts as JSON for one agent.

    Args:
        agent: Agent identifier.
        task_hint: One-sentence description of the current task. When provided,
            each fact gains a ``relevance_score`` and facts are sorted by
            relevance descending so the most pertinent context appears first.
            Also enables the caller to skip memory-dependent steps quickly
            when the returned ``summary.has_data`` is ``false``.
    """
    _chk_agent(agent)
    root = _workspace_root()
    branch = _current_branch(root) or ""
    return _shared_memory_dump(agent, root, branch, _SESSION_ID, task_hint)


@mcp.tool()
def memory_prune(
    agent: str | None = None,
    scope: str | None = None,
    max_age_days: float | None = None,
) -> str:
    """Delete expired rows and optionally stale rows, keeping FTS in sync."""
    if agent is not None:
        _chk_agent(agent)
    if scope is not None:
        _chk_scope(scope)
    return _shared_memory_prune(agent, scope, max_age_days, _workspace_root())


@mcp.tool()
def rule_add(
    description: str, rule_type: str,
    agent: str | None = None, scope: str = "workspace", branch: str | None = None,
) -> str:
    """Add an authoritative rule that agents must follow."""
    _chk_rule_type(rule_type)
    _chk_agent(agent)
    _chk_branch(branch)
    _chk_rule_scope(scope)
    _chk_str_len("description", description)
    root = _workspace_root()
    if scope == "branch" and branch is None:
        branch = _advisory_branch(scope, root)
    return _shared_rule_add(description, rule_type, agent, scope, branch, root)


@mcp.tool()
def rule_list(agent: str | None = None, scope: str = "workspace") -> str:
    """List authoritative rules for an agent and scope."""
    _chk_agent(agent)
    _chk_rule_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    return _shared_rule_list(agent, scope, branch, root)


@mcp.tool()
def rule_remove(rule_id: int) -> str:
    """Delete a rule by id."""
    return _shared_rule_remove(rule_id, _workspace_root())


@mcp.tool()
def diary_add(
    agent: str, entry: str, scope: str = "workspace", tags: str = "",
) -> str:
    """Append a decision or action entry to the agent diary."""
    _chk_agent(agent)
    _chk_scope(scope)
    _chk_str_len("entry", entry)
    _chk_str_len("tags", tags)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    session_id = _SESSION_ID if scope == "session" else ""
    return _shared_diary_add(agent, entry, scope, tags, branch, session_id, root)


@mcp.tool()
def diary_get(
    agent: str, scope: str = "workspace", limit: int = 20, tag: str | None = None,
) -> str:
    """Retrieve recent diary entries, newest first."""
    _chk_agent(agent)
    _chk_scope(scope)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    session_id = _SESSION_ID if scope == "session" else ""
    return _shared_diary_get(agent, scope, limit, tag, branch, session_id, root)


@mcp.tool()
def diary_search(
    agent: str, query: str, scope: str = "workspace",
    limit: int = 20, include_agents: list[str] | None = None,
) -> str:
    """FTS5 full-text search across diary entries and tags."""
    _chk_agent(agent)
    _chk_scope(scope)
    for a in (include_agents or []):
        _chk_agent(a)
    root = _workspace_root()
    branch = _advisory_branch(scope, root)
    session_id = _SESSION_ID if scope == "session" else ""
    return _shared_diary_search(agent, query, scope, limit, include_agents, branch, session_id, root)


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
