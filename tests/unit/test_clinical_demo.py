from __future__ import annotations

import unittest

from core.clinical_demo import analyze_prescription_text


class TestClinicalDemo(unittest.TestCase):
    def test_full_demo_analysis(self) -> None:
        result = analyze_prescription_text(
            "Diagnosis: fever\nTab Paracetamol 500mg 1-0-1 x 3 days\nTab Cetirizine 10mg HS x 5 days"
        )
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["confidence"]["level"], "medium")
        self.assertEqual(len(result["medicine_knowledge"]), 2)
        self.assertIn("patient_summary", result)

    def test_language_selection_localizes_patient_output(self) -> None:
        result = analyze_prescription_text("Tab Paracetamol 500mg OD x 3 days", "hi")
        self.assertEqual(result["language"], "hi")
        self.assertEqual(result["ui_labels"]["dose"], "खुराक")
        self.assertEqual(result["parsed_prescription"]["medicines"][0]["frequency"], "दिन में एक बार")
        self.assertIn("OD का अर्थ", result["parsed_prescription"]["medicines"][0]["frequency_explanation"])


if __name__ == "__main__":
    unittest.main()
