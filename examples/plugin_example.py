from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.plugins import ClinicalAIPlugin, PluginRegistry


class ExampleParserPlugin(ClinicalAIPlugin):
    name = "example-parser"
    version = "0.1.0"
    capabilities = {"parsers"}

    def register(self, registry: PluginRegistry) -> None:
        registry.register("parsers", self.name, self)

    def parse(self, text: str) -> dict:
        return {"resourceType": "Bundle", "type": "collection", "entry": [], "source_text_length": len(text)}


if __name__ == "__main__":
    registry = PluginRegistry()
    ExampleParserPlugin().register(registry)
    print(registry.capabilities())
