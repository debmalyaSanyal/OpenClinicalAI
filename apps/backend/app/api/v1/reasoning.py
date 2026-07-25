from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("")
def reason(payload: dict) -> dict:
    return {"status": "accepted", "message": "Reasoning orchestration is plugin-backed and evidence-first.", "input_keys": sorted(payload.keys())}
