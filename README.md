# agentstore

מקום מרכזי לשמירת סוכנים ייחודיים (כמו Grok Bot) וחיבורם לכל שירות דרך API.
A central store for unique agents, each connectable to any service over HTTP.

## מבנה
```
agents/<id>/agent.json   # הגדרת סוכן: אישיות (system_prompt), מודל, קונקטורים
agentstore/registry.py   # טעינה, ולידציה ושמירה
agentstore/runtime.py    # הרצת סוכן + זיכרון שיחה לכל session
agentstore/connectors/   # webhook, telegram, slack, discord (קל להוסיף עוד)
agentstore/server.py     # REST API
```

## שימוש
```bash
export ANTHROPIC_API_KEY=...        # מפתח ה-LLM
export AGENTSTORE_API_KEY=...       # מפתח לגישה ל-API (בלעדיו ה-API סגור)
python -m agentstore list
python -m agentstore new my-agent --prompt "You are ..."
python -m agentstore chat grok-bot "שלום"
python -m agentstore serve --port 8080
```

### API
| Method | Path | תיאור |
|---|---|---|
| GET | `/agents`, `/agents/{id}` | רשימה / סוכן בודד |
| PUT / DELETE | `/agents/{id}` | יצירה-החלפה / מחיקה |
| POST | `/agents/{id}/chat` | `{"text","session"}` → `{"reply"}` |
| POST | `/hooks/{connector}/{id}` | Webhook נכנס משירות חיצוני |

ניהול וצ'אט דורשים `Authorization: Bearer $AGENTSTORE_API_KEY`. ה-hooks מאומתים על ידי הקונקטור (סוד משותף / חתימת Slack / secret token של Telegram).

## הוספת סוכן
צרו `agents/<id>/agent.json` (ראו `agents/grok-bot`). סודות **לא** נשמרים בקובץ — רק שמות משתני סביבה (`token_env`, `secret_env`).

## קונקטור חדש
צרו קובץ ב-`agentstore/connectors/`, ירשו מ-`Connector`, ממשו `parse` (+`verify`/`send`), וסמנו ב-`@register("name")`. ייבאו אותו ב-`connectors/__init__.py`.

## בדיקות
`python -m unittest discover -s tests -t .`
