# Plugin Guide

Plugins implement `ClinicalAIPlugin` and register one or more capabilities with `PluginRegistry`.

```python
from core.plugins import ClinicalAIPlugin, PluginRegistry

class MyPlugin(ClinicalAIPlugin):
    name = "my-plugin"
    version = "0.1.0"
    capabilities = {"parsers"}

    def register(self, registry: PluginRegistry) -> None:
        registry.register("parsers", self.name, self)
```

Stable capability buckets:

- OCR engines
- Medical parsers
- Medical databases
- Report analyzers
- Speech engines
- Translation engines
- Reminder engines
- Hospital/insurance integrations
- Custom AI models
