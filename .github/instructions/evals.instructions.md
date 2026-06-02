---
name: Eval Files
applyTo: "evals/**/*.yaml,packs/**/evals/**/*.yaml"
description: "Conventions for eval.yaml suite files and task files in this workspace — naming, schema, graders, and coverage"
---

# Eval File Instructions

## eval.yaml

- `name` must be `"<SuiteName>-eval"` where `SuiteName` matches the parent directory name exactly.
- `description` must state what agent or skill behavior the suite evaluates.
- `graders` must include at least one entry; use `text` (with a `pattern` config key accepting a regex) for content presence checks and `behavior` (with a `max_tokens` config key) for response length bounds. An `llm` grader type is available for semantic correctness; consult `tools/xanadEval/xanadEval.py` for its config fields as they are not standardised here.
- `tasks` must contain exactly one glob entry (`- "tasks/*.yaml"`); do not list individual task files by name.

## Task files

- File `id` must match the filename without the `.yaml` extension.
- Every task must include `description`, `prompt`, and at least one of `expected` or `expected_absent`.
- Every task must have a `tags` list that includes `smoke`.
- Name task files by role: `basic-invocation.yaml` for the primary happy-path invocation of a skill; `positive-trigger-N.yaml` to verify an agent or skill triggers on a matching prompt; `negative-trigger-N.yaml` to verify it does not trigger on unrelated input.
- Ensure `tasks/` contains at least one task file; an empty directory produces zero tests with no diagnostic error.

## Coverage requirements

- Every agent eval suite must contain at least `positive-trigger-1.yaml`, `positive-trigger-2.yaml`, and `negative-trigger-1.yaml`.
- Every skill eval suite must contain at least `basic-invocation.yaml`, `positive-trigger-1.yaml`, and `negative-trigger-1.yaml`.
- `expected` values are plain literal strings matched against the response — no escaping needed; dots and special characters are treated as literals. `expected_absent` values are regex patterns that must not appear in the response — escape literal dots and special characters (e.g., use `\.` for a literal dot in a version string like `1\.2\.3`).
- Pack eval suites under `packs/**/evals/` follow the same coverage requirements as top-level suites.
