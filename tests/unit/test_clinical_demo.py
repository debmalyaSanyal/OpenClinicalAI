from __future__ import annotations

import unittest

from core.clinical_demo import (
    analyze_lab_report_text,
    analyze_prescription_text,
    answer_document_question,
    answer_prescription_question,
)


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

    def test_chatbot_answers_timing_questions(self) -> None:
        result = answer_prescription_question(
            "Tab Paracetamol 500mg BD x 3 days",
            "What does BD mean?",
        )
        self.assertEqual(result["status"], "complete")
        self.assertIn("twice daily", result["answer"])
        self.assertIn("BD means", result["answer"])

    def test_chatbot_answers_food_timing_directly(self) -> None:
        result = answer_prescription_question(
            "Rx: Dexamethasone - 4 mg PO daily for 3 day(s)",
            "can i have the medicine after breakfast",
        )
        self.assertEqual(result["answer"], "Dexamethasone: the prescription does not say before or after food.")
        self.assertEqual(result["safety_note"], "")

    def test_chatbot_answers_dose_directly(self) -> None:
        result = answer_prescription_question(
            "Rx: Dexamethasone - 4 mg PO daily for 3 day(s)",
            "how much should I have",
        )
        self.assertEqual(result["answer"], "Dexamethasone: 4 mg for 3 days.")
        self.assertEqual(result["safety_note"], "")

    def test_analyzes_blood_report_values(self) -> None:
        result = analyze_lab_report_text(
            """
            Hemoglobin 11.2 g/dL
            WBC 12.5 10^3/uL
            Platelets 240 10^3/uL
            Fasting Glucose 142 mg/dL
            Creatinine 1.0 mg/dL
            """
        )
        self.assertEqual(result["document_type"], "lab_report")
        self.assertEqual(len(result["lab_tests"]), 5)
        self.assertEqual(result["lab_tests"][0]["status"], "low")
        self.assertEqual(result["lab_tests"][1]["status"], "high")

    def test_chatbot_answers_lab_report_questions(self) -> None:
        result = answer_document_question(
            "Hemoglobin 11.2 g/dL\nWBC 12.5 10^3/uL",
            "which values are abnormal?",
            "lab_report",
        )
        self.assertIn("Hemoglobin: 11.2 g/dL is low", result["answer"])
        self.assertIn("WBC: 12.5 10^3/uL is high", result["answer"])

    def test_chatbot_rejects_sugary_food_when_sugar_is_high(self) -> None:
        result = answer_document_question(
            "Fasting Glucose 142 mg/dL\nHemoglobin 11.2 g/dL",
            "can I have some mangoes for lunch",
            "lab_report",
        )
        self.assertIn("Negative", result["answer"])
        self.assertIn("sugar value is high", result["answer"])
        self.assertIn("Glucose 142 mg/dL", result["answer"])
        self.assertIn("Hemoglobin: 11.2 g/dL is low", result["answer"])

    def test_indian_reference_profile_is_returned(self) -> None:
        result = analyze_lab_report_text("LDL 120 mg/dL", reference_profile="india")
        self.assertEqual(result["reference_profile"], "India-oriented adult demo ranges")
        self.assertEqual(result["lab_tests"][0]["status"], "normal")

    def test_prescription_mode_surfaces_embedded_report_values(self) -> None:
        result = analyze_prescription_text(
            """
            Pregabid CR 82.5 a ah I
            8 Lumia 60K once monthly
            hba1c-8.083
            hb-8.4
            """
        )
        self.assertEqual([medicine["name"] for medicine in result["parsed_prescription"]["medicines"]], ["Pregabid", "Lumia"])
        self.assertEqual([value["name"] for value in result["clinical_values"]], ["Hemoglobin", "HBA1C"])
        self.assertIn("HBA1C 8.083 %", result["patient_summary"])


if __name__ == "__main__":
    unittest.main()
