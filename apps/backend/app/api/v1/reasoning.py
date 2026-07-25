from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import analyze_prescription_text

router = APIRouter()


@router.post("")
def reason(payload: dict) -> dict:
    return analyze_prescription_text(str(payload.get("text", payload.get("question", ""))))
