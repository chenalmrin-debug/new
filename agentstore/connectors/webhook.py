from .base import Connector, register


@register("webhook")
class Webhook(Connector):
    """Generic REST connector: POST {"text": "...", "session": "..."} -> {"reply": "..."}.
    Auth: header X-Webhook-Secret must equal the env var named by config.secret_env."""

    def parse(self, payload):
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            return None
        return text, str(payload.get("session", "default")), None
