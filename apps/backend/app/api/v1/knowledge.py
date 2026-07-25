from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/retrieve")
def retrieve(payload: dict) -> dict:
    return {"status": "accepted", "message": "Knowledge retrieval plugins should return evidence packages.", "query": payload.get("query", "")}
