"""Runs an agent: system prompt + per-session memory -> LLM provider -> reply."""
from __future__ import annotations

import json
import os
import urllib.request
from collections import defaultdict
from typing import Callable

from .registry import AgentSpec

API_URL = "https://api.anthropic.com/v1/messages"

# provider(spec, messages) -> reply text. Replaceable for tests or other LLM vendors.
Provider = Callable[[AgentSpec, list], str]


def anthropic_provider(spec: AgentSpec, messages: list) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    body = json.dumps({
        "model": spec.model,
        "max_tokens": spec.max_tokens,
        "temperature": spec.temperature,
        "system": spec.system_prompt,
        "messages": messages,
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


class Runtime:
    def __init__(self, provider: Provider = anthropic_provider):
        self.provider = provider
        self._history: dict[tuple, list] = defaultdict(list)

    def chat(self, spec: AgentSpec, text: str, session: str = "default") -> str:
        hist = self._history[(spec.id, session)]
        hist.append({"role": "user", "content": text})
        window = hist[-2 * spec.memory_turns:] if spec.memory_turns else hist[-1:]
        while window and window[0]["role"] != "user":  # window must start with a user turn
            window = window[1:]
        try:
            reply = self.provider(spec, window)
        except Exception:
            hist.pop()  # don't keep an unanswered turn
            raise
        hist.append({"role": "assistant", "content": reply})
        del hist[:-2 * max(spec.memory_turns, 1)]
        return reply
