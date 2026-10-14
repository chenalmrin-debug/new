from .base import Connector, post_json, register


@register("telegram")
class Telegram(Connector):
    """config: token_env, secret_env (set as secret_token in setWebhook)."""

    def verify(self, headers, body):
        import hmac, os
        expected = os.environ.get(self.config.get("secret_env") or "")
        return bool(expected) and hmac.compare_digest(
            headers.get("x-telegram-bot-api-secret-token", ""), expected)

    def parse(self, payload):
        msg = payload.get("message") or {}
        text, chat = msg.get("text"), (msg.get("chat") or {}).get("id")
        if not text or chat is None:
            return None
        return text, f"tg-{chat}", chat

    def send(self, target, text):
        post_json(f"https://api.telegram.org/bot{self.secret('token')}/sendMessage",
                  {"chat_id": target, "text": text})
        return {"ok": True}
