---
name: extensionManagement
description: "Use when: discovering, recommending, installing, enabling, disabling, or uninstalling VS Code extensions by intent or known extension ID."
version: "1.0"
license: MIT
---

# Extension Management

> Skill metadata: version "1.0"; tags [vscode, extensions, marketplace, install, manage]; recommended tools [vscode_searchExtensions_internal, run_vscode_command, vscode_askQuestions].

Procedural skill for managing VS Code extensions: recommending extensions by user intent, resolving human names to extension IDs, and performing install, enable, disable, and uninstall operations through VS Code commands.

## When to use

- When a user asks which extension to use for a given task or language
- When a user asks to install, enable, disable, or uninstall a VS Code extension
- When an extension ID is unknown and must be discovered from the marketplace
- When the user wants to install multiple extensions in a single operation

## When NOT to use

- When the user already has the exact extension ID and only wants to install — the built-in `install-vscode-extension` skill handles that without search
- When the request is about workspace package manager dependencies (npm, pip, etc.) — prefer the `deps` agent
- When the request is to develop or build a VS Code extension — this skill manages installed extensions, not extension source code

---

## Module 1 — Discover And Recommend

1. **Determine the user's intent.**
   - If the user named a specific extension or provided a known ID, proceed to Module 2.
   - If the user described a task, problem, or language (e.g. "I need something for Python formatting"), extract 2–4 search keywords from that description.

2. **Search the marketplace.**
   - Call `vscode_searchExtensions_internal` with the extracted keywords and, when the category is clear, the matching `category` filter (e.g. `Formatters`, `Linters`, `Testing`, `AI`, `Debuggers`).
   - If the search returns zero results, broaden by dropping the category filter and retrying with keywords only. If still no results, report the failure and ask the user to supply the extension ID directly.

3. **Select and present candidates.**
   - Filter results to extensions that are clearly relevant to the stated intent.
   - Present up to 3 candidates with: display name, publisher, extension ID, a one-sentence description, and install count or rating where available.
   - If only one result is clearly correct, state the recommendation directly without listing alternatives.
   - Ask the user to confirm the target before proceeding to Module 3 when multiple candidates are presented.

---

## Module 2 — Identify And Validate

4. **Resolve the extension ID.**
   - Use the confirmed search result, user-supplied ID, or a known mapping (e.g. "Python extension" → `ms-python.python`).
   - Verify the ID follows the `publisher.extensionName` format. If not, return to step 2.

5. **Determine the version flag.**
   - If the current environment is VS Code Insiders, set `installPreReleaseVersion: true`.
   - Otherwise set `installPreReleaseVersion: false` unless the user explicitly requests the pre-release version.

---

## Module 3 — Execute

6. **Route to the correct command.**

   | User intent | VS Code command |
   | --- | --- |
   | Install | `workbench.extensions.installExtension` |
   | Enable (globally) | `workbench.extensions.enableExtension` |
   | Disable (globally or workspace) | `workbench.extensions.disableExtension` |
   | Uninstall | `workbench.extensions.uninstallExtension` |

7. **Confirm before destructive operations.**
   - For **uninstall** or **disable** (both of which affect the user's environment persistently), call `vscode_askQuestions` first with the exact extension name and ID and the scope of the action before calling `run_vscode_command`.
   - Do not confirm for install or enable — these are reversible without data loss.

8. **Execute via `run_vscode_command`.**
   - For install: pass args `[extensionId, { enable: true, installPreReleaseVersion: <bool> }]` and `skipCheck: true`.
   - For all other commands: pass `[extensionId]` and `skipCheck: true`.
   - For multiple extensions, execute one `run_vscode_command` call per extension in sequence; do not batch into a single call.

9. **Report the outcome.**
   - State the extension name, ID, action taken, and whether it succeeded or failed.
   - If the command fails, report the exact error and suggest either verifying the ID via marketplace search or asking the user to perform the action manually from the Extensions panel.

---

## Verify

- [ ] Extension was located by marketplace search or a confirmed ID before any command was executed — search was not skipped unless the user supplied a known ID
- [ ] Candidates were presented and user intent was confirmed before acting when multiple results were returned
- [ ] The `installPreReleaseVersion` flag reflects the current VS Code variant (Insiders = true, Stable = false) unless the user explicitly overrode it
- [ ] Uninstall and disable operations were preceded by a `vscode_askQuestions` confirmation with extension name, ID, and action scope
- [ ] Each extension was installed or managed in a separate `run_vscode_command` call with `skipCheck: true`
- [ ] Outcome (success or failure with error detail) was reported for every operation
