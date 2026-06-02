---
name: sessionDiagnostics
description: "Use when: diagnosing unexpected Copilot Chat behavior, slow responses, missing instructions or skills, tool call failures, extension conflicts, MCP registration issues, or workspace configuration problems."
version: "1.0"
license: MIT
---

# Session Diagnostics

> Skill metadata: version "1.0"; tags [diagnostics, troubleshoot, copilot, vscode, mcp, logs]; recommended tools [run_in_terminal, read_file, file_search, grep_search, run_vscode_command].

Procedural skill for diagnosing unexpected behavior in VS Code Copilot Chat. Triage is tiered from the most local evidence source to the broadest; evidence is always collected before a conclusion is stated.

> Session log directory for this conversation: `{{VSCODE_TARGET_SESSION_LOG}}`
>
> Log files live outside the workspace. **Use `run_in_terminal` with `grep`/`jq` to read them — `grep_search` cannot access files outside the workspace.**

## When to use

- When Copilot Chat behaves unexpectedly: wrong output, skipped instructions, missing skills or agents, blocked tools, slow responses
- When an MCP server tool is not appearing or is failing to register
- When a workspace hook, instruction, or custom agent is not being applied
- When a tool call fails repeatedly and the cause is unclear

## When NOT to use

- When the failure is clearly a code bug in the user's project — prefer `debugger`
- When the task is to review or improve a surface file's content — prefer `agenticReview`
- When the lifecycle install state is the suspected cause — prefer `lifecycleAudit` first

---

## Module 1 — Classify The Symptom

1. **Map the reported symptom to a tier** before collecting any evidence:

   | Symptom | Tier | Primary evidence source |
   | --- | --- | --- |
   | Wrong output, skipped step, unexpected tool call, slow response | **1 — Chat surface** | `main.jsonl` debug log |
   | Instruction, skill, or agent not loaded | **1 — Chat surface** | `main.jsonl` discovery events |
   | Tool call errored or produced wrong result | **1 — Chat surface** | `main.jsonl` tool_call events |
   | Extension not responding, command unavailable | **2 — Extension** | VS Code diagnostics command |
   | MCP server tool not appearing, tool call returns not-found | **2 — Extension** | VS Code diagnostics + MCP config file |
   | Hook not firing, instruction `applyTo` not matching | **3 — Workspace config** | `.github/` directory layout + frontmatter |
   | Multiple unrelated anomalies at once | **All tiers** | Investigate Tier 1 first, then widen |

2. **State the tier explicitly** before collecting evidence. Proceed through tiers in order; do not jump ahead to later tiers.

---

## Module 2 — Investigate By Tier

### Tier 1 — Chat Debug Logs

3. **Locate the log file.**
   - The session log path is provided above as `{{VSCODE_TARGET_SESSION_LOG}}`.
   - Check file size first: `ls -lh "{{VSCODE_TARGET_SESSION_LOG}}/main.jsonl"` (or `(Get-Item ...).Length` on Windows). If the file exceeds 20 MB, use streaming tools only — never read the entire file.

4. **Triage via targeted grep/jq** (do not read the full file):

   | Question | Command (Linux/macOS) |
   | --- | --- |
   | Any errors? | `grep '"status":"error"' main.jsonl` |
   | Slow events? | `jq -c 'select(.dur > 5000)' main.jsonl` |
   | What loaded? | `grep '"type":"discovery"' main.jsonl` |
   | What tools were called? | `grep '"type":"tool_call"' main.jsonl` |
   | What model was used? | `grep '"type":"llm_request"' main.jsonl \| head -5` |

   On Windows without `jq`, use: `node -e "require('fs').readFileSync('main.jsonl','utf8').split('\n').filter(Boolean).map(JSON.parse).filter(e => e.status==='error').forEach(e => console.log(JSON.stringify(e)))"`

5. **Read only relevant slices** with `read_file` once line numbers are known from grep output. Never read the entire log file.

6. **Check for network/auth issues** if repeated timeouts or 401/403 errors appear in the log:
   - Run VS Code command `github.copilot.debug.collectDiagnostics` via `run_vscode_command` with `skipCheck: true`.
   - Read the returned string for auth status, proxy config, and reachability.

### Tier 2 — Extension And MCP

7. **Run VS Code diagnostics** for authentication, network, and extension state:
   - `run_vscode_command` with command `github.copilot.debug.collectDiagnostics` and `skipCheck: true`.

8. **Check MCP server registration** if a tool is not appearing:
   - Use `file_search` for `**/.vscode/mcp.json` and `**/.github/mcp.json` in the workspace.
   - Read the found config file with `read_file` and verify the server entry, command path, and args.
   - Check whether the server is listed in the VS Code diagnostics output under MCP servers.

9. **Check extension conflicts** — if the symptom is a command not found or an unexpected command remapping:
   - Identify which extension owns the command or setting from the error message.
   - Note the extension ID and version from the diagnostics output.

### Tier 3 — Workspace Configuration

10. **Audit the `.github/` directory layout** for instruction, agent, skill, or hook issues:
    - `file_search` for `.github/**/*.instructions.md`, `.github/agents/*.agent.md`, `skills/**/SKILL.md`, `.github/hooks/*.json`
    - Verify filenames and paths match expected conventions.

11. **Check `applyTo` patterns** on any instruction or hook that should have fired:
    - `read_file` the frontmatter of the relevant file.
    - Confirm the `applyTo` glob would match the file path the agent was working on.

12. **Check hook trigger and script path** for non-firing hooks:
    - Read the hook JSON and verify `event`, `command`, and that the script path exists using `file_search`.

---

## Module 3 — Report Findings

13. **Report each finding in this structure:**
    ```
    Finding: <short description>
    Tier: <1 | 2 | 3>
    Evidence: <log line, config value, or diagnostic field that supports this>
    Confidence: <High | Medium | Low>
    Remediation: <concrete next step>
    ```

14. **Order findings by impact** — findings that block all agent behavior before findings that affect specific tools.

15. **State what was NOT investigated** if any tier was skipped or evidence was unavailable, and explain why.

---

## Verify

- [ ] Symptom was classified to a tier before any log or file was read
- [ ] Log files were accessed with `run_in_terminal` grep/jq commands — `grep_search` was not used for log files
- [ ] File size was checked before reading any log file larger than a few MB
- [ ] VS Code diagnostics command was run for Tier 2 symptoms
- [ ] Each finding includes evidence source, confidence level, and a concrete remediation step
- [ ] Skipped tiers were explicitly noted with a reason
