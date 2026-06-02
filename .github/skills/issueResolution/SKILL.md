---
name: issueResolution
description: "Use when: fetching, classifying, and resolving a GitHub issue — covering intake triage, duplicate search, code location, fix proposal, and PR readiness assessment."
version: "1.0"
license: MIT
---

# Issue Resolution

> Skill metadata: version "1.0"; tags [github, issues, fix, triage, search]; recommended tools [mcp_xanadgithub_get_issue, mcp_xanadgithub_list_issues, mcp_xanadgithub_search_code, grep_search, semantic_search, vscode_listCodeUsages].

Procedural skill for resolving GitHub issues end-to-end: intake and classify the issue, search for duplicates or related work, locate the relevant code, propose a concrete fix, and assess PR readiness. Each step is completed before the next begins; no fix is proposed before the code is located.

## When to use

- When asked to investigate, triage, or fix a GitHub issue by number or URL
- When asked to search for issues matching a description before filing a new one
- When a fix needs to be grounded in actual code locations rather than assumed

## When NOT to use

- When the task is purely reviewing a PR's diff — prefer the `review` agent
- When the issue is a Copilot Chat or VS Code behavior issue — prefer `sessionDiagnostics`
- When no GitHub tools are available and the issue details have not been provided in context — ask the user to paste the issue body before proceeding

---

## Module 1 — Intake And Classify

1. **Fetch the issue** using the best available GitHub tool:
   - Prefer `mcp_xanadgithub_get_issue` when the `xanadgithub` MCP server is connected.
   - Fall back to `github-pull-request_issue_fetch` when the GitHub PR extension tool is available.
   - If neither is available, ask the user to paste the issue title, body, and label list before continuing.

2. **Extract key fields:** title, body, labels, assignee, milestone, linked PRs, and open/closed state.

3. **Classify the issue type** before proposing any action:

   | Classification | Indicators | Next step |
   | --- | --- | --- |
   | **Bug** | Describes unexpected behavior, includes steps to reproduce or an error message | Module 2 → Module 3 (reproduce) → Module 4 |
   | **Enhancement** | Requests new behavior, no current breakage described | Module 2 → Module 4 (design note first) |
   | **Question / Support** | Asks how something works, no clear broken state | Answer from code/docs; do not write a fix |
   | **Unclear** | Insufficient detail to classify | Ask one clarifying question before continuing |

4. **Do not propose a fix for a Question issue.** State the answer with file/line references and stop.

---

## Module 2 — Search For Related Issues And Prior Work

5. **Search for duplicate or related open issues** before writing any code:
   - Extract 2–4 keywords from the issue title and body.
   - Call `mcp_xanadgithub_list_issues` or `github-pull-request_doSearch` with a focused query (e.g. `repo:owner/name is:issue state:open <keywords>`).
   - If neither GitHub search tool is available, use `grep_search` across the workspace for the error message or key symbol name.

6. **Check for existing linked PRs** on the issue. If an open PR already addresses the issue, report it and stop — do not write a duplicate fix.

7. **Search code history** for prior attempts using `mcp_xanadgithub_search_code` or `grep_search` for the symbol, function name, or error string from the issue.

8. **Report related findings** to the user before proceeding to Module 3. If a duplicate exists, surface it and ask whether to continue with a new fix.

---

## Module 3 — Locate The Code

9. **Identify the affected symbol, file, or code path** from the issue's description and error message.

10. **Locate using the narrowest available method:**

    | What you have | Method |
    | --- | --- |
    | Exact function or class name | `vscode_listCodeUsages` with the symbol name |
    | Error message text or log string | `grep_search` with `isRegexp: false` |
    | Conceptual description of the behavior | `semantic_search` |
    | File name or path hint in the issue | `file_search` |

11. **Confirm the location** — read the relevant lines with `read_file` around the identified code region. Do not write a fix based on search results alone without reading the actual code.

12. **Trace the call path** for bugs where the issue manifests in one place but originates elsewhere:
    - Use `vscode_listCodeUsages` to find callers or producers of the broken value.
    - Read no more than 2 levels up the call chain before proposing the fix.

---

## Module 4 — Propose The Fix

13. **Write the fix** targeting the root cause location confirmed in Module 3, not a downstream symptom.

14. **Fix requirements:**
    - Reference actual file paths with line numbers (use `[path/file.ts](path/file.ts#L10)` format)
    - Include the minimal change — do not refactor surrounding code unless it is the direct cause
    - For bugs: the fix must address the reproduction path from the issue, not just silence the error
    - For enhancements: state the design decision and any interface change before showing the code

15. **Assess PR readiness:**

    | Question | If yes |
    | --- | --- |
    | Does the fix change a public API or function signature? | Note that callers must be updated; check with `vscode_listCodeUsages` |
    | Does the fix touch authentication, authorization, input handling, or data storage? | Flag as a security boundary — recommend a `secureReview` before merging |
    | Does the fix require a new test? | State the test case name, what it asserts, and where it belongs |
    | Does the fix depend on a config change or migration? | Note the config key and default value |

16. **Summarize** the fix with: issue type, root cause location (file + line), change description, and PR readiness status (ready / needs test / needs security review / needs caller updates).

---

## Verify

- [ ] Issue was fetched or provided in context before any fix was proposed
- [ ] Issue type was classified (Bug / Enhancement / Question / Unclear) before Module 3
- [ ] Related issues and existing linked PRs were checked before writing code
- [ ] Code location was confirmed by reading actual lines — fix was not written from search results alone
- [ ] Fix targets the root cause file and line, not a downstream symptom
- [ ] PR readiness was assessed: security boundary, test requirement, and caller impact were each addressed
