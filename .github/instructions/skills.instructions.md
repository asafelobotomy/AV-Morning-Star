---
name: Skill Files
applyTo: "skills/**/SKILL.md,packs/**/skills/**/SKILL.md"
description: "Conventions for SKILL.md files in this workspace — frontmatter, section structure, and verification discipline"
---

# Skill File Instructions

## Frontmatter

- Every `SKILL.md` must include `name` and `description` in the YAML frontmatter.
- `name` must match the parent directory name exactly.
- `description` must be a single sentence beginning with `Use when:`.

## Required sections

- Sections must appear in this order: `## When to use`, `## When NOT to use`, then the step or module body, then `## Verify`.
- `## When NOT to use` must include at least one entry covering the case where a more-specific skill should be preferred instead.
- `## Verify` must be a Markdown checklist (`- [ ]` items); each item must reference an observable outcome, not merely a completed step (e.g., "`inspect` output has been read this session", not "Step 3 was completed").
- The skill body must open with a metadata comment block: `> Skill metadata: version "X.Y"; tags [...]; recommended tools [...]`. Start new skills at `version "1.0"`. Increment the minor version for each behavioural change (updated steps, new modules, changed fallback paths); increment the major version for breaking structural changes (e.g. removing a module or the `## Verify` section); do not bump the version for prose-only edits. List only tools the skill's steps explicitly call in `recommended tools`.

## Skill types

Skills are either **procedural** or **reference**. Declare the type with the body's opening sentence or context:

- **Procedural skills** describe a step-by-step workflow. Use `## Steps` or `## Module N` headings. Steps must be numbered; each step must have a clear action and either a success criterion or an explicit fallback path. xanadEval's `workflow structure present` check applies to procedural skills.
- **Reference skills** provide domain conventions, decision tables, and checklists — not a linear procedure. Use domain-specific section headings (e.g. `## Pipeline stage model`, `## STRIDE categories`). xanadEval's `workflow structure present` check does not apply to reference skills; `module-count` warnings are advisory only.

Pack skills under `packs/*/skills/` are typically reference skills unless they contain a `## Steps` section.

## Authoring rules

- Multi-module skills must contain 2–6 `## Module N` headings (xanadEval `module-count` threshold). Skills using `## Steps` instead of `## Module N` are exempt from this check — xanadEval's `module-count: 0` advisory can be ignored for `## Steps`-based skills.
- External dependencies (MCP servers, other agents, APIs) must each have a documented failure path or fallback.
- Do not embed agent routing decisions inside a skill — a skill describes a procedure, not a routing table.
