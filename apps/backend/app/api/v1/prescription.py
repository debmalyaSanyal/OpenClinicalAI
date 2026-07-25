from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("")
def parse_prescription(payload: dict) -> dict:
    return {
        "status": "accepted",
        "message": "Prescription pipeline endpoint registered. Install OCR/parser plugins to process documents.",
        "input_keys": sorted(payload.keys()),
    }
