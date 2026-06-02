---
name: lifecycleAudit
description: "Use when: checking xanadAssistant workspace health, install status, repair reasons, or lockfile validity before proposing install, update, repair, or restore operations."
version: "1.3"
license: MIT
---

# Lifecycle Health Check

> Skill metadata: version "1.3"; tags [xanadAssistant, lifecycle, inspect, repair, lockfile]; recommended tools [lifecycle_inspect, lifecycle_check, lifecycle_plan_setup, run_in_terminal].

Systematic lifecycle state review before any install, update, repair, or factory-restore operation.

## When to use

- Before proposing any `setup`, `update`, `repair`, or `factory-restore` operation
- When a workspace's install state is unknown, stale, or suspect
- When `repairReasons` or `needsMigration` are referenced in a conversation

## When NOT to use

- During an already-in-progress lifecycle operation — proceed without auditing mid-flight
- When the user explicitly requests a specific operation and state is already known
- When executing a lifecycle command or remediation workflow — use the `xanadLifecycle` agent instead of this preflight audit skill

## Module 1 — Inspect And Read Health

> `<xanad-root>` is the directory containing `xanadAssistant.py`. Use `.` when running from the package root (self-hosted install) or the absolute path to the installed package otherwise. If `xanadAssistant.py` is not found, halt and report the error to the user before proceeding.

1. **Inspect** — prefer `lifecycle_inspect` when the `xanadTools` MCP server is connected and can resolve the package source; otherwise run `python3 xanadAssistant.py inspect --workspace . --package-root <xanad-root> --json`. Verify `installState` and `manifestSummary`. If the tool or command exits non-zero, halt and report the error before proceeding.

2. **Check** — prefer `lifecycle_check` when the `xanadTools` MCP server is connected and can resolve the package source; otherwise run `python3 xanadAssistant.py health-check --workspace . --package-root <xanad-root> --json`. Read `status`, `warnings`, and `result.summary`. Treat exit `7` as a normal drift signal to classify, not as an execution failure. Halt only on other non-zero exits. If you need machine-readable `repairReasons`, prefer `lifecycle_plan_setup` only for setup planning and use `python3 xanadAssistant.py plan repair --workspace . --package-root <xanad-root> --json` for repair reasons rather than inferring them from `health-check`.

## Module 2 — Classify And Report

3. **Classify the state** — the `needsMigration: true` row takes priority over all other rows:

   | `installState` | `health-check.status` / `plan.repairReasons` | Action |
   | --- | --- | --- |
   | `installed` | `clean` and no plan repair reasons | Proceed with intended operation |
   | `installed` | `drift` or non-empty plan repair reasons | Run `repair` first, then re-check |
   | `not-installed` | any | Run `setup` |
   | any + `needsMigration: true` | any | Run `repair` to migrate lockfile shape first |

4. **Surface findings** — report `installState`, `selectedPacks`, `profile`, `health-check.status`, and any plan `repairReasons` before proposing the intended operation. Prefer `plan` output over ad-hoc file edits. If `warnings` contains memory health codes, classify them: `memory_db_missing` is first-run-safe (info only); `memory_mcp_missing` or `memory_mcp_unregistered` means the memory hook is not registered — propose a repair; `memory_db_schema_corrupt` means the DB is corrupted — propose immediate repair.

5. **Ownership** — keep managed vs skipped surfaces explicit. Do not edit files with `ownership: local` without first running `plan` and reviewing the output.

## Verify

- [ ] `inspect` output has been read this session
- [ ] `check.status` is `clean` or the user has acknowledged the reported drift
- [ ] plan `repairReasons` is empty or the user has acknowledged them
- [ ] `needsMigration` is false or repair has been run
- [ ] Memory health warnings (`memory_mcp_missing`, `memory_mcp_unregistered`, `memory_db_schema_corrupt`) are noted if present — a missing DB is first-run-safe (info only); missing hook or corrupt schema warrants proposing a repair operation to the user
