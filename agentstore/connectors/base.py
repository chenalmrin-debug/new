from __future__ import annotations

import hmac
import json
import os
import urllib.request

REGISTRY: dict[str, type["Connector"]] = {}


def register(name: str):
    def deco(cls):
        REGISTRY[name] = cls
        cls.name = name
        return cls
    return deco


def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else {}


class Connector:
    name = ""

    def __init__(self, config: dict):
        self.config = config

    def secret(self, key: str) -> str:
        """Resolve config['<key>_env'] to the env var's value."""
        var = self.config.get(f"{key}_env")
        value = os.environ.get(var or "")
        if not value:
            raise RuntimeError(f"{self.name}: env var for '{key}' is not set")
        return value

    def verify(self, headers: dict, body: bytes) -> bool:
        """Check the inbound request is authentic. Default: shared secret in X-Webhook-Secret."""
        expected = os.environ.get(self.config.get("secret_env") or "")
        if not expected:
            return False  # fail closed
        return hmac.compare_digest(headers.get("x-webhook-secret", ""), expected)

    def parse(self, payload: dict):
        """Return (text, session_id, reply_target) or None to ignore the event."""
        raise NotImplementedError

    def send(self, target, text: str) -> dict | None:
        """Deliver the reply. Return a dict to be used as the HTTP response body, or None."""
        return {"reply": text}
