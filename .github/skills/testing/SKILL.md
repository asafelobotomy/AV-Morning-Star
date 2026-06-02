---
name: testing
description: "Use when: running targeted or full tests in any workspace, choosing the safest available test command, summarizing test results, or deciding when to hand failing tests to debugger."
version: "1.5"
license: MIT
---

# Testing

> Skill metadata: version "1.5"; tags [testing, validation, mcp, workflow, generic]; recommended tools [testing_show_key_commands, testing_show_capabilities, testing_list_tests, testing_run_tests, testing_parse_coverage, run_in_terminal].

Procedural skill for running tests through the workspace's declared testing apparatus before, during, or after code changes.

## When to use

- When a task needs targeted tests, full tests, or a validation summary
- When the workspace's test command should be discovered instead of assumed
- When deciding whether a failing test needs debugger handoff

## When NOT to use

- When the user asks for a full CI-equivalent pre-commit or pre-push gate — prefer `ciPreflight`
- When tests are already failing and root-cause diagnosis is the main task — prefer `debugger`
- When the task is test coverage adequacy or regression-risk review — prefer `review`
- When strict Red-Green-Refactor coaching is needed and the TDD pack is installed — prefer the TDD pack skill or prompt
- When the workspace has no declared test apparatus and the task is to define one — prefer direct repo maintenance or documentation updates over this runtime workflow

## Steps

1. Discover the workspace test apparatus.
   - Prefer `testing_show_key_commands` from the `workspaceTesting` MCP server.
   - Confirm a declared `Run tests` command exists and is not `(not detected)`.
   - When available, call `testing_show_capabilities` to learn the detected runner, timeout policy, typed-targeting mode, and coverage support before choosing flags or scope.
   - If `workspaceTesting` is unavailable, read the workspace instructions or project docs for the documented test command; do not invent a shell command.

2. Choose the narrowest useful scope.
   - If `testing_show_capabilities` reports `supportsTestDiscovery=true`, prefer `testing_list_tests` to confirm available test ids before building a targeted run.
   - For a localized code change, run targeted tests first with safe argv-style target arguments only when `supportsTypedTargets=true`; recognized runner families may still report `false` for compound command shapes such as `python -m unittest discover ...`.
   - For shared infrastructure, generated surfaces, or task completion, run the full declared test command.
   - If `supportsTypedTargets=false` or target arguments are uncertain or framework-specific, prefer a full run over guessing unsafe flags.

3. Execute through the safest available runner.
   - Prefer `testing_list_tests(targetFiles=[...])` only when capability discovery explicitly reports safe test discovery.
   - Prefer `testing_run_tests(scope="default", extraArgs=[...])` for targeted runs.
   - Treat `targetFiles` and `testNames` as valid only when `supportsTypedTargets=true`; otherwise expect `workspaceTesting` to reject them and use `scope="full"` or explicit `extraArgs` instead.
   - Prefer `testing_run_tests(scope="full")` for full runs.
   - Use the documented native command only when the `workspaceTesting` server is unavailable.
   - Do not use arbitrary command strings, shell interpolation, pipes, redirects, or commands requiring secrets unless the workspace documentation explicitly requires them.

4. Summarize the result in an agent-readable form.
   - Report status, command or tool used, exit code, `runnerExitReason` when present, and the relevant stdout/stderr tail.
   - Identify first failing test, failing file, or failure class when the output makes that clear.
   - State whether the check is targeted, full, skipped, unavailable, or blocked.

5. Parse coverage artifacts when they are part of the workspace's test apparatus.
   - Prefer `testing_parse_coverage(coveragePath="coverage.xml")` for Cobertura-style coverage output when the file exists or is documented by the workspace.
   - Report percent covered, valid/covered line counts, and zero-coverage files when available.
   - If no coverage artifact is declared or produced, state that coverage was not assessed rather than guessing.

6. Act on failures deliberately.
   - If the failure is clearly caused by the current edit slice, fix that slice and rerun the same test.
   - If root cause is unclear, delegate to `debugger` with the exact command, output tail, changed files, and why the test was selected.
   - If a test cannot run because the workspace lacks a declared test command, report the missing apparatus and suggest adding one to workspace instructions.

## Verify

- [ ] A declared workspace test command or explicit unavailable state has been observed this session
- [ ] `testing_show_capabilities` was used or an explicit reason was given for skipping capability discovery
- [ ] `testing_list_tests` was used only when `supportsTestDiscovery=true`, or its absence was justified by capability output
- [ ] `workspaceTesting.testing_run_tests` was preferred when available, with documented native fallback only when needed
- [ ] Targeted runs used safe argv-style arguments; full runs used the command exactly
- [ ] Output summary includes status, command/tool, exit code when available, `runnerExitReason` when present, and relevant output tail
- [ ] Coverage artifact was parsed with `testing_parse_coverage` when present or explicitly reported as not assessed
- [ ] Failing tests were either repaired in the current slice or handed to `debugger` with exact evidence
