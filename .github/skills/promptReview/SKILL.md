---
name: promptReview
description: "Use when: reviewing .prompt.md files for contradictions, ambiguity, persona consistency, cognitive load, coverage gaps, and composition conflicts before merge or troubleshooting."
version: "1.0"
license: MIT
---

# Prompt Review

> Skill metadata: version "1.0"; tags [review, prompt, quality]; recommended tools [read_file, file_search, grep_search].

Review a `.prompt.md` file as a single-invocation Copilot prompt: frontmatter, trigger clarity, dependency handling, output contract, and fit with pack or workspace conventions.

## When to use

- Before merging a new or changed `.prompt.md` file
- When a prompt routes unexpectedly or produces inconsistent output
- When pack prompt quality needs a targeted review without auditing agents or skills

## When NOT to use

- When reviewing `.agent.md`, `SKILL.md`, or `.instructions.md` files — use `agenticReview` instead
- When authoring or fixing a prompt directly — use the agent customization workflow or edit from the prompt convention
- During an already-running lifecycle operation — let `xanadLifecycle` complete first

## Module 1 — Frontmatter And Routing

1. Verify YAML frontmatter parses and includes `mode` and `description`.
2. Check that `description` names the user-visible task and contains routing keywords.
3. Confirm `mode` matches the prompt's behavior: `ask` for chat workflows, another supported mode only when documented.
4. Report any stale name, duplicate identity, or description that points to a different prompt.

## Module 2 — Contradictions

1. Compare the prompt's task statement, instructions, and output format for conflicting requirements.
2. Check whether dependency instructions negate local fallback or output rules.
3. Flag any step that asks for missing information after also requiring immediate output.
4. Report each conflict with the smallest text change that resolves it.

## Module 3 — Ambiguity And Inputs

1. Identify vague inputs, undefined terms, or placeholders without collection rules.
2. Check whether optional inputs have a default behavior when omitted.
3. Verify the prompt tells the agent when to ask a question before producing output.
4. Suggest precise replacement text for each ambiguous instruction.

## Module 4 — Dependency And Fallback Coverage

1. List every referenced skill, tool, pack convention, or external source.
2. Confirm each dependency has an explicit fallback if unavailable.
3. Check that local instructions are sufficient to proceed when a dependency is missing.
4. Flag hard dependency failures as High severity when the prompt cannot complete without them.

## Module 5 — Output Contract

1. Verify the output format is concrete enough to test with string or schema assertions.
2. Check that success and zero-finding paths are both defined when the prompt reviews or audits content.
3. Confirm the requested format does not conflict with style constraints from referenced skills.
4. Suggest eval expectations for any required section or verdict that lacks coverage.

## Module 6 — Composition Fit

1. Compare the prompt with related pack skills, pack prompts, and instruction files it references.
2. Flag duplicate rules that have drifted from their source skill or pack convention.
3. Check that the prompt stays in its pack's domain and does not silently route adjacent work.
4. End with a merge decision: `ready to merge`, `needs revision before merge`, or `block: restructure required`.

## Verify

- [ ] Frontmatter parses and `description` matches the prompt's actual task
- [ ] All six modules produced findings or an explicit no-findings statement
- [ ] Every referenced skill or tool has an availability fallback or a reported coverage gap
- [ ] Output contract includes required sections, zero-finding behavior, and a merge decision
- [ ] Any suggested eval expectations are tied to observable output strings or schema fields
