from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("")
def search(payload: dict) -> dict:
    return {"status": "accepted", "message": "Search backends are configurable: Qdrant, FAISS, PostgreSQL.", "query": payload.get("query", "")}
