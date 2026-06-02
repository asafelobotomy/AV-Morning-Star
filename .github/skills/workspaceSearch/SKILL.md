---
name: workspaceSearch
description: "Use when: choosing the right search strategy for a workspace query, executing and refining searches, and acting on results — covering exact text, regex, semantic, file-path, and VS Code search-panel modes."
version: "1.0"
license: MIT
---

# Workspace Search

> Skill metadata: version "1.0"; tags [search, workspace, grep, semantic, file-discovery]; recommended tools [grep_search, semantic_search, file_search, run_vscode_command, vscode_listCodeUsages].

Procedural skill for selecting, executing, and acting on workspace searches. Different intents require different tools; using the wrong tool produces noisy or empty results. This skill routes to the correct method first, refines on poor results, and dispatches findings to the next action.

## When to use

- When a workspace query could be answered by more than one search method and the best fit is unclear
- When initial search results are empty, too noisy, or scoped incorrectly
- When search results need to be acted on: navigation, refactoring, documentation, or task extraction
- When the VS Code Search panel's current results need to be read into context

## When NOT to use

- When the search intent is already clear and a single `grep_search` or `semantic_search` call is obviously sufficient — call it directly without this skill
- When searching external sources (GitHub issues, web) — prefer `issueResolution` or web tools
- When the task is refactoring found symbols across a workspace — prefer `pylance-refactoring` if available

---

## Module 1 — Choose The Search Method

1. **Identify the search intent** from the query or task description.

   | Intent | Best method |
   | --- | --- |
   | Find an exact string, identifier, or known phrase | `grep_search` (plain text, `isRegexp: false`) |
   | Find a pattern, regex, or multiple alternatives | `grep_search` (regex, `isRegexp: true`, use `\|` alternation) |
   | Find by concept, purpose, or natural-language description | `semantic_search` |
   | Find files by name, extension, or path pattern | `file_search` with glob pattern |
   | Read the current VS Code Search panel results | `run_vscode_command` with `search.action.getSearchResults` and `skipCheck: true` |
   | Find all usages of a known symbol | `vscode_listCodeUsages` |

2. **Scope the search before executing** — don't search the whole workspace when a narrower scope is valid:
   - Use `includePattern` in `grep_search` to restrict to a directory or file type (e.g. `src/**`, `**/*.py`)
   - Use `maxResults` only when the result count is expected to be large and you only need confirmation, not a full list

3. **Batch independent search methods** — if the intent requires both exact-text and semantic results, issue both calls in the same turn rather than sequentially.

---

## Module 2 — Execute And Refine

4. **Execute the chosen search method.**

5. **Evaluate the results quality** before acting:

   | Symptom | Refinement |
   | --- | --- |
   | Zero results (exact search) | Verify spelling; try a shorter substring; switch to regex with alternation |
   | Zero results (semantic search) | Try a more concrete query; switch to `grep_search` for a key term from the concept |
   | Zero results (file search) | Broaden glob (e.g. `**/foo*` instead of `src/**/foo.ts`) |
   | Too many results (>50 relevant-looking matches) | Add `includePattern` to narrow scope; make the pattern more specific |
   | Results from generated/vendor dirs | Add exclusion note in query; results from `node_modules`, `dist`, `.venv` should be filtered out before acting |
   | Results span multiple unrelated areas | Run a second scoped search per area and treat each result set separately |

6. **Do not re-run the same search twice.** If the first result is poor, apply one refinement and execute once more. If the second result is still poor, report the failure with the attempted queries and stop.

---

## Module 3 — Act On Results

7. **Dispatch results to the appropriate next action:**

   | Goal | Action |
   | --- | --- |
   | Navigate to a definition or declaration | Use `vscode_listCodeUsages` on the symbol name with a matched line as `lineContent` |
   | Count occurrences for a summary | Report count and representative file list — do not enumerate all matches |
   | Identify files for a refactoring scope | Pass the file list as the target scope to the refactoring step |
   | Extract a pattern for documentation | Quote the first 2–3 representative matches with file links |
   | Build a task list from results | Group matches by directory or module boundary |
   | Determine whether a symbol is unused | Check that usage count is zero across all result methods before concluding |

8. **Format file references as workspace-relative links** using `[path/file.ts](path/file.ts#L10)` notation when surfacing results to the user.

---

## Verify

- [ ] Search method was chosen based on the stated intent using the routing table — the search-panel fallback was not used by default
- [ ] `includePattern` was used or explicitly ruled out before executing a broad search
- [ ] At least one refinement was attempted when initial results were empty or had more than 50 noisy matches
- [ ] Results were not re-searched with the identical query after the first failure
- [ ] Findings were dispatched to a concrete next action or explicitly surfaced as the final output
- [ ] Results from generated or vendor directories were identified and excluded from conclusions
