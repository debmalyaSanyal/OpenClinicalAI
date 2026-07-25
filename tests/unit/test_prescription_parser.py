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
        self.assertEqual(result["medicines"][1]["frequency_abbreviation"], "BD")
        self.assertIn("twice daily", result["medicines"][1]["frequency_explanation"])

    def test_parses_rx_colon_and_continuation_duration(self) -> None:
        result = parse_prescription_text(
            """
            DentalRx
            Rx: Dexamethasone - 4 mg PO daily
            for 3 day(s)
            Quantity: 3x4 mg tabs
            """
        )
        self.assertEqual(len(result["medicines"]), 1)
        self.assertEqual(result["medicines"][0]["name"], "Dexamethasone")
        self.assertEqual(result["medicines"][0]["dose"], "4 mg")
        self.assertEqual(result["medicines"][0]["frequency"], "once daily")
        self.assertEqual(result["medicines"][0]["duration"], "3 days")

    def test_explains_common_short_forms(self) -> None:
        result = parse_prescription_text(
            """
            Tab Paracetamol 500mg OD x 3 days
            Tab Cetirizine 10mg HS x 5 days
            Syrup Pantoprazole 40mg AC x 5 days
            """
        )
        self.assertEqual(result["medicines"][0]["frequency_explanation"], "OD means once daily, usually one dose in a day.")
        self.assertEqual(result["medicines"][1]["frequency"], "at bedtime")
        self.assertEqual(result["medicines"][2]["frequency"], "before food")


if __name__ == "__main__":
    unittest.main()
