from __future__ import annotations

import unittest

from core.prescription_parser import parse_prescription_text


class TestPrescriptionParser(unittest.TestCase):
    def test_parses_sample_prescription_text(self) -> None:
        result = parse_prescription_text(
            """
            Diagnosis: fever with throat infection
            Tab Paracetamol 500mg 1-0-1 x 3 days
            Cap Amoxicillin 500mg BD x 5 days
            Tab Cetirizine 10mg HS x 5 days
            """
        )
        self.assertEqual(result["status"], "parsed")
        self.assertEqual(len(result["medicines"]), 3)
        self.assertEqual(result["medicines"][0]["name"], "Paracetamol")
        self.assertEqual(result["medicines"][0]["frequency"], "morning and night")


if __name__ == "__main__":
    unittest.main()
