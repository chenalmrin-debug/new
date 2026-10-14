---
name: new-agent
description: Create a new unique agent (persona + tools + service connections) in this repo's agent store. Use when the user asks to add, define or save a new agent.
---

Create `.claude/agents/<name>.md` from `templates/agent.md.tmpl`.

1. Ask only for what is missing: purpose, persona/voice, which services it must reach.
2. File name = `name` field, lowercase with dashes. Do not overwrite an existing agent without asking.
3. Give it the minimum `tools`. Read-only unless the user asks for write access.
4. For each service: prefer an MCP server (add it to `.mcp.json`, secrets via `${ENV_VAR}`), otherwise document the HTTP API in `docs/services.md` and use `api-connector`.
5. Add the agent to the table in `docs/agents.md`.
6. Never write secret values into any file.
