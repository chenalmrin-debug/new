from .base import Connector, post_json, register


@register("discord")
class Discord(Connector):
    """Relay connector: your Discord bot POSTs {"text","channel"} (with X-Webhook-Secret);
    the reply is returned in the response AND posted to config.webhook_url_env (Discord webhook)."""

    def parse(self, payload):
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            return None
        return text, f"discord-{payload.get('channel', 'default')}", None

    def send(self, target, text):
        if self.config.get("webhook_url_env"):
            post_json(self.secret("webhook_url"), {"content": text[:2000]})
        return {"reply": text}
