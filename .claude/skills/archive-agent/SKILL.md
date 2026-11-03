---
name: archive-agent
description: Retire an agent without deleting it (move it to agents/archive/). Use when the user wants to disable, retire or shelve an agent.
---

1. Find the agent in `.claude/agents/` or `agents/drafts/`.
2. `git mv` it to `agents/archive/<name>.md` (never delete).
3. Update its row in `docs/agents.md` to status `archived`.
