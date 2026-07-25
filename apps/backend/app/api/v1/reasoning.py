from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import analyze_prescription_text, answer_prescription_question

router = APIRouter()


@router.post("")
def reason(payload: dict) -> dict:
    return analyze_prescription_text(
        str(payload.get("text", payload.get("question", ""))),
        str(payload.get("language", "en")),
    )


@router.post("/chat")
def chat(payload: dict) -> dict:
    return answer_prescription_question(
        str(payload.get("text", "")),
        str(payload.get("question", "")),
        str(payload.get("language", "en")),
    )
