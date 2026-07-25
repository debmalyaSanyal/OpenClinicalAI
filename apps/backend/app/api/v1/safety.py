from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import evaluate_safety

router = APIRouter()


@router.post("/validate")
def validate_safety(payload: dict) -> dict:
    text = str(payload.get("text", ""))
    medicines = payload.get("medicines", [])
    return {"status": "complete", "safety_review": evaluate_safety(text, medicines)}
