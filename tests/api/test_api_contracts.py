from __future__ import annotations

import unittest
import importlib.util

create_app = None
if importlib.util.find_spec("fastapi"):
    from apps.backend.app.main import create_app


@unittest.skipIf(create_app is None, "FastAPI is not installed in this runtime.")
class TestAPIContracts(unittest.TestCase):
    def test_app_routes_registered(self) -> None:
        app = create_app()
        paths = {route.path for route in app.routes}
        self.assertIn("/v1/health", paths)
        self.assertIn("/v1/fhir/validate", paths)
        self.assertIn("/v1/prescription", paths)


if __name__ == "__main__":
    unittest.main()
