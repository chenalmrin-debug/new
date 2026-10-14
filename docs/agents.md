# Agent store

אזור מסודר ליצירה ושמירה של סוכנים ייעודיים. אפשר ליצור סוכן עוד לפני שהמטרה שלו הוגדרה.

## מבנה
| מיקום | משמעות | נטען ע"י Claude? |
|---|---|---|
| `agents/drafts/` | טיוטות - מטרה עדיין לא הוגדרה | לא |
| `.claude/agents/` | סוכנים פעילים | כן |
| `agents/archive/` | סוכנים שיצאו משימוש (לא נמחקים) | לא |
| `templates/agent.md.tmpl` | תבנית לסוכן חדש | – |

## תהליך
1. `/new-agent <שם>` - יוצר טיוטה (מטרה = `TBD` אם לא ידועה).
2. עורכים את `agents/drafts/<שם>.md`: מטרה, אישיות, כלים, שירותים.
3. `/activate-agent <שם>` - מעביר ל-`.claude/agents/` (מופיע בסשן חדש).
4. `/archive-agent <שם>` - מעביר לארכיון כשלא צריך יותר.

## אינדקס
| סוכן | סטטוס | תיאור | שירותים |
|---|---|---|---|
| `grok-bot` | active | פרסונה עוקצנית וישירה בסגנון Grok | – |
| `api-connector` | active | קריאות HTTP API לכל שירות (לפי `docs/services.md`) | כל API |
| `gils-work` | draft | שכתוב שורות מקובץ הרשמות ללשונית "התחייבות מוסדית" (דילוג על קיימות, ללא עריכה במקום) | – |

## חיבור לשירותים
1. **MCP (מועדף)** - הוסיפו שרת ל-`.mcp.json` והגבילו סוכן אליו עם `mcpServers:` ב-frontmatter:
   ```json
   {"mcpServers": {"github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/",
                              "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}}
   ```
2. **HTTP API ישיר** - תעדו ב-`docs/services.md`; `api-connector` מבצע את הקריאות.

סודות: רק משתני סביבה (`${VAR}`), לעולם לא בקבצים או ב-commit. פעולות שמשנות מצב דורשות אישור המשתמש.
