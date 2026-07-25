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

    def test_parses_case_history_medicine_table_rows(self) -> None:
        result = parse_prescription_text(
            """
            Other Medication:
            SLNo. OTHER MEDICINE DOSE PURPOSE
            1 Stamlo 5 od htn
            2 Tazloc 40 od htn
            3 Atrovas 10mg od chol
            4 Lupoxa OD od RA
            5 COLLASHOT C2 PLUS od pain
            6 Macvestin 500 mg od RA
            7 Pregabid CR 82.5 od pain
            8 Lumia 60K once monthly vitd3
            9 Primolut-N od menstruation
            """
        )
        names = [medicine["name"] for medicine in result["medicines"]]
        self.assertIn("Stamlo", names)
        self.assertIn("Tazloc", names)
        self.assertIn("Atrovas", names)
        self.assertIn("Primolut-N", names)
        self.assertEqual(result["medicines"][0]["dose"], "5")
        self.assertEqual(result["medicines"][0]["frequency"], "once daily")
        self.assertGreaterEqual(len(result["medicines"]), 8)


if __name__ == "__main__":
    unittest.main()
