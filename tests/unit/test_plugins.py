from __future__ import annotations

import unittest

from core.plugins import PluginRegistry
from examples.plugin_example import ExampleParserPlugin


class TestPlugins(unittest.TestCase):
    def test_register_parser(self) -> None:
        registry = PluginRegistry()
        ExampleParserPlugin().register(registry)
        self.assertIn("example-parser", registry.capabilities()["parsers"])


if __name__ == "__main__":
    unittest.main()
