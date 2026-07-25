from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    name: str
    task: str
    provider: str
    config: dict[str, Any]
    enabled: bool = True


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ModelSpec] = {}

    def register(self, spec: ModelSpec) -> None:
        self._models[f"{spec.task}:{spec.name}"] = spec

    def get(self, task: str, name: str | None = None) -> ModelSpec | None:
        if name:
            return self._models.get(f"{task}:{name}")
        candidates = [spec for key, spec in self._models.items() if key.startswith(f"{task}:") and spec.enabled]
        return candidates[0] if candidates else None

    def list(self, task: str | None = None) -> list[ModelSpec]:
        return [spec for spec in self._models.values() if task is None or spec.task == task]
