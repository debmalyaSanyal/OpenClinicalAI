from __future__ import annotations

import unittest

from core.model_registry import ModelRegistry, ModelSpec


class TestModelRegistry(unittest.TestCase):
    def test_register_and_get(self) -> None:
        registry = ModelRegistry()
        registry.register(ModelSpec(name="bge", task="embedding", provider="sentence-transformers", config={}))
        self.assertEqual(registry.get("embedding").name, "bge")


if __name__ == "__main__":
    unittest.main()
