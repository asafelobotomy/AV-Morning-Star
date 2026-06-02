---
name: Agent Files
applyTo: "agents/*.agent.md"
description: "Conventions for .agent.md files in this workspace — frontmatter schema, body structure, and routing discipline"
---

# Agent File Instructions

## Frontmatter

- Every `.agent.md` file must declare all of: `name`, `description`, `argument-hint`, `model`, `tools`, `agents`, `user-invocable`.
- `target:` — optional field; set to `vscode` for all workspace agents. Omit if the agent targets a different host environment.
- `name` must match the filename case-insensitively — `review` → `review.agent.md`.
- `description` must start with `"Use when:"` followed by trigger phrases; keep it in sync with the routing tables in `copilot-instructions.md` and `AGENTS.md`.
- `argument-hint` must describe what a caller should pass — use imperative phrasing ("Describe the task…").
- `model` is a preference-ordered list; the first entry is the default, subsequent entries are fallbacks ordered by closer task-fit before lighter-but-less-capable models.
- `tools` lists every tool the body explicitly uses. Name MCP tools by their function name only (e.g., `memory_dump`, not `mcp_memory_memory_dump`). The tools list is a hard enforcement boundary — unlisted tools are inaccessible to the agent at runtime.
- `user-invocable: true` for agents a user can invoke directly; `false` for subagent-only agents.
- `agents` lists only delegatee agents the body explicitly delegates to; do not list agents the body never references.

## Body

- Open with `You are the <Name> agent.` followed immediately by `Your role:` as a single sentence.
- Include a `Do not use this agent for:` section listing at least three out-of-scope scenarios.
- Include an `On every invocation` section with numbered steps defining the agent's procedure.
- For agents that perform destructive operations (e.g., file deletions, git reset --hard, force pushes), include a `Risk tiers` table covering every destructive operation mentioned in the body.
- Call `memory_dump(agent="<name>", task_hint="<one-sentence task description>")` as the first `On every invocation` step for any agent that has a `## Memory` section.
- Document each handoff to a delegatee agent with a one-line rationale inline (e.g., in the `On every invocation` steps or guidelines section).
