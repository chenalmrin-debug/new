import hashlib
import hmac
import time

from .base import Connector, post_json, register


@register("slack")
class Slack(Connector):
    """Slack Events API. config: token_env (bot token), secret_env (signing secret)."""

    def verify(self, headers, body):
        import os
        secret = os.environ.get(self.config.get("secret_env") or "")
        ts = headers.get("x-slack-request-timestamp", "0")
        if not secret or not ts.isdigit() or abs(time.time() - int(ts)) > 300:
            return False
        digest = hmac.new(secret.encode(), b"v0:" + ts.encode() + b":" + body, hashlib.sha256).hexdigest()
        return hmac.compare_digest("v0=" + digest, headers.get("x-slack-signature", ""))

    def parse(self, payload):
        if payload.get("type") == "url_verification":
            return None
        ev = payload.get("event") or {}
        if ev.get("type") not in ("message", "app_mention") or ev.get("bot_id") or not ev.get("text"):
            return None
        return ev["text"], f"slack-{ev.get('channel')}", ev.get("channel")

    def send(self, target, text):
        post_json("https://slack.com/api/chat.postMessage", {"channel": target, "text": text},
                  {"authorization": f"Bearer {self.secret('token')}"})
        return {"ok": True}
