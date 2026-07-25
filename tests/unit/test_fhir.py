from __future__ import annotations

import unittest

from core.fhir.bundle import FHIRBundle
from core.fhir.resources import FHIRResource
from core.fhir.validation import FHIRValidationError, validate_resource


class TestFHIR(unittest.TestCase):
    def test_validate_patient(self) -> None:
        validate_resource({"resourceType": "Patient", "id": "p1"})

    def test_reject_missing_resource_type(self) -> None:
        with self.assertRaises(FHIRValidationError):
            validate_resource({"id": "p1"})

    def test_reject_unknown_resource_type(self) -> None:
        with self.assertRaises(FHIRValidationError):
            validate_resource({"resourceType": "Unknown"})

    def test_resource_round_trip(self) -> None:
        resource = FHIRResource.from_dict({"resourceType": "Observation", "id": "o1", "status": "final"})
        self.assertEqual(resource.to_fhir_json()["status"], "final")

    def test_bundle(self) -> None:
        resource = FHIRResource.from_dict({"resourceType": "Patient", "id": "p1"})
        bundle = FHIRBundle.from_resources([resource])
        self.assertEqual(bundle.resourceType, "Bundle")
        self.assertEqual(bundle.entry[0]["resource"]["resourceType"], "Patient")


if __name__ == "__main__":
    unittest.main()
