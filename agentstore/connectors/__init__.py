"""Connectors turn an inbound service webhook into (text, session) and send the reply back.

Secrets are never stored in agent.json; config holds env var NAMES, e.g. {"token_env": "TELEGRAM_TOKEN"}.
"""
from .base import Connector, REGISTRY
from . import webhook, telegram, slack, discord  # noqa: F401  (register on import)

__all__ = ["Connector", "REGISTRY"]
