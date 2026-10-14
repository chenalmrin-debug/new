"""Agent registry: each agent lives in agents/<id>/agent.json and is validated on load."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "agents"


class ValidationError(ValueError):
    pass


@dataclass
class AgentSpec:
    id: str
    name: str
    system_prompt: str
    description: str = ""
    model: str = "claude-sonnet-5-5"
    max_tokens: int = 1024
    temperature: float = 1.0
    # connector name -> config (secrets are env var NAMES, never values)
    connectors: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)
    memory_turns: int = 20  # conversation turns kept per session

    @classmethod
    def from_dict(cls, data: dict) -> "AgentSpec":
        if not isinstance(data, dict):
            raise ValidationError("agent spec must be an object")
        for key in ("id", "name", "system_prompt"):
            if not isinstance(data.get(key), str) or not data[key].strip():
                raise ValidationError(f"missing or empty field: {key}")
        if not ID_RE.match(data["id"]):
            raise ValidationError("id must be lowercase letters, digits and dashes")
        unknown = set(data) - set(cls.__dataclass_fields__)
        if unknown:
            raise ValidationError(f"unknown fields: {sorted(unknown)}")
        spec = cls(**data)
        if not isinstance(spec.connectors, dict):
            raise ValidationError("connectors must be an object")
        if not 1 <= spec.max_tokens <= 64000:
            raise ValidationError("max_tokens out of range")
        if not 0 <= spec.temperature <= 1:
            raise ValidationError("temperature must be between 0 and 1")
        if spec.memory_turns < 0:
            raise ValidationError("memory_turns must be >= 0")
        return spec

    def to_dict(self) -> dict:
        return asdict(self)


class Registry:
    def __init__(self, root: Path | str = DEFAULT_ROOT):
        self.root = Path(root)

    def _path(self, agent_id: str) -> Path:
        if not ID_RE.match(agent_id):
            raise ValidationError("invalid agent id")
        return self.root / agent_id / "agent.json"

    def list(self) -> list[AgentSpec]:
        if not self.root.exists():
            return []
        return [self.get(p.parent.name) for p in sorted(self.root.glob("*/agent.json"))]

    def get(self, agent_id: str) -> AgentSpec:
        path = self._path(agent_id)
        if not path.exists():
            raise KeyError(agent_id)
        spec = AgentSpec.from_dict(json.loads(path.read_text(encoding="utf-8")))
        if spec.id != agent_id:
            raise ValidationError(f"id '{spec.id}' does not match folder '{agent_id}'")
        return spec

    def save(self, spec: AgentSpec) -> Path:
        spec = AgentSpec.from_dict(spec.to_dict())  # re-validate
        path = self._path(spec.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def delete(self, agent_id: str) -> None:
        path = self._path(agent_id)
        if not path.exists():
            raise KeyError(agent_id)
        path.unlink()
        try:
            path.parent.rmdir()
        except OSError:
            pass  # folder has extra files (docs, knowledge) - keep them
