from __future__ import annotations

from fastapi import APIRouter

from core.clinical_demo import lookup_medicine

router = APIRouter()


@router.post("/retrieve")
def retrieve(payload: dict) -> dict:
    query = str(payload.get("query", ""))
    return {"status": "complete", "query": query, "result": lookup_medicine(query)}
