from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import analyze_prescription_text

router = APIRouter()


@router.post("")
def analyze_report(payload: dict) -> dict:
    analysis = analyze_prescription_text(str(payload.get("text", "")), str(payload.get("language", "en")))
    return {
        "status": "complete",
        "report_type": "prescription_summary",
        "summary": analysis["patient_summary"],
        "safety_review": analysis["safety_review"],
    }
