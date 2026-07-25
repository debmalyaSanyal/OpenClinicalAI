from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/{patient_id}")
def get_patient(patient_id: str) -> dict:
    return {"patient_id": patient_id, "message": "Patient repository adapter not configured."}
