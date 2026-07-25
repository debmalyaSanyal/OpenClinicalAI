from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/validate")
def validate_safety(payload: dict) -> dict:
    return {"status": "accepted", "message": "Safety guardrail plugins validate questions and responses.", "input_keys": sorted(payload.keys())}
