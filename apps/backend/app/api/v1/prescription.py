from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("")
def parse_prescription(payload: dict) -> dict:
    return {
        "status": "accepted",
        "message": "Prescription pipeline endpoint registered. Install OCR/parser plugins to process documents.",
        "input_keys": sorted(payload.keys()),
    }


@router.post("/upload")
async def upload_prescription(file: UploadFile = File(...)) -> dict:
    contents = await file.read()
    return {
        "status": "received",
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "message": (
            "Prescription upload is working. OCR/model inference is not bundled in this "
            "lightweight Vercel deployment yet."
        ),
        "next_step": "Connect a hosted OCR/model service to return extracted medicines and instructions.",
    }
