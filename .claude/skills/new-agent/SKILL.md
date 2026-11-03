---
name: new-agent
description: Create a dedicated agent as a DRAFT in the agent store, even when its goal is not defined yet. Use when the user asks to add, define, create or save a new agent.
---

Drafts live in `agents/drafts/<name>.md` and are NOT loaded by Claude Code until activated.

1. Ask only for what is missing. The goal may be left as `TBD`; a name is enough to start.
2. Copy `templates/agent.md.tmpl` to `agents/drafts/<name>.md`; name = lowercase with dashes, equal to the `name` field. Never overwrite an existing agent (check drafts, `.claude/agents/`, `agents/archive/`).
3. Fill in only what the user gave. Leave the rest `TBD`; do not invent goals or personas.
4. Minimum `tools`, read-only unless the user asks otherwise.
5. Services: prefer an MCP server (`.mcp.json`, secrets as `${ENV_VAR}`); otherwise document the HTTP API in `docs/services.md`. Never write secret values anywhere.
6. Add a row to the table in `docs/agents.md` with status `draft`.
7. Tell the user the draft is saved and that `/activate-agent <name>` enables it once the goal is set.
