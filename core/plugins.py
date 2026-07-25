from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol


class Plugin(Protocol):
    name: str
    version: str

    def register(self, registry: "PluginRegistry") -> None:
        ...


class ClinicalAIPlugin(ABC):
    name: str
    version: str
    capabilities: set[str]

    @abstractmethod
    def register(self, registry: "PluginRegistry") -> None:
        raise NotImplementedError


@dataclass
class PluginRegistry:
    ocr_engines: dict[str, Any] = field(default_factory=dict)
    parsers: dict[str, Any] = field(default_factory=dict)
    medical_databases: dict[str, Any] = field(default_factory=dict)
    report_analyzers: dict[str, Any] = field(default_factory=dict)
    speech_engines: dict[str, Any] = field(default_factory=dict)
    translation_engines: dict[str, Any] = field(default_factory=dict)
    reminder_engines: dict[str, Any] = field(default_factory=dict)
    integrations: dict[str, Any] = field(default_factory=dict)
    ai_models: dict[str, Any] = field(default_factory=dict)

    def register(self, capability: str, name: str, implementation: Any) -> None:
        bucket = getattr(self, capability)
        bucket[name] = implementation

    def capabilities(self) -> dict[str, list[str]]:
        return {
            key: sorted(value.keys())
            for key, value in self.__dict__.items()
            if isinstance(value, dict)
        }
