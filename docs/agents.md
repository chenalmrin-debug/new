# Agent store

כל הסוכנים הייחודיים נשמרים כאן, כקבצי Markdown ב-`.claude/agents/` ש-Claude Code טוען אוטומטית.

## סוכנים
| סוכן | תיאור | כלים | שירותים |
|---|---|---|---|
| `grok-bot` | פרסונה עוקצנית וישירה בסגנון Grok | קריאה + חיפוש | – |
| `api-connector` | קריאות HTTP API לכל שירות | Bash, Read, WebFetch | כל API (לפי `docs/services.md`) |

## הוספת סוכן
`/new-agent` (skill), או העתיקו את `templates/agent.md.tmpl` ל-`.claude/agents/<name>.md`.
שדה `description` קובע מתי Claude יאציל לסוכן - כתבו אותו ספציפי.

## חיבור לשירותים
1. **MCP (מועדף)** - הוסיפו שרת ל-`.mcp.json`, והגבילו סוכן מסוים אליו עם `mcpServers:` ב-frontmatter שלו:
   ```json
   {"mcpServers": {"github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/",
                              "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}}
   ```
2. **HTTP API ישיר** - תעדו את השירות ב-`docs/services.md`; הסוכן `api-connector` מבצע את הקריאות.

סודות: רק במשתני סביבה (`${VAR}`), לעולם לא בקבצים או ב-commit.
פעולות שמשנות מצב (שליחה, יצירה, מחיקה) דורשות אישור המשתמש.
