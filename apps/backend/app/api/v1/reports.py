from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("")
def analyze_report(payload: dict) -> dict:
    return {"status": "accepted", "message": "Report analyzer plugins can be registered here.", "input_keys": sorted(payload.keys())}
