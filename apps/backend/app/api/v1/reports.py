from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import analyze_lab_report_text

router = APIRouter()


@router.post("")
def analyze_report(payload: dict) -> dict:
    return analyze_lab_report_text(str(payload.get("text", "")), str(payload.get("language", "en")))
