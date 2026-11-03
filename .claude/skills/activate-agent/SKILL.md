---
name: activate-agent
description: Promote a draft agent to active (move agents/drafts/<name>.md to .claude/agents/). Use when the user says an agent is ready, its goal is defined, or asks to enable/activate it.
---

1. Read `agents/drafts/<name>.md`. If `## Goal`, `description` or persona still say `TBD`, ask the user to fill them in (or fill them from what they say) before continuing.
2. `git mv agents/drafts/<name>.md .claude/agents/<name>.md` (fail if the target exists).
3. Update the row in `docs/agents.md` to status `active`.
4. Tell the user a new session (or `/agents` reload) is needed to see it.
