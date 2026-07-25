from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from core.prescription_parser import parse_prescription_text

router = APIRouter()


@router.post("")
def parse_prescription(payload: dict) -> dict:
    text = str(payload.get("text", ""))
    if text.strip():
        return parse_prescription_text(text)
    return {"status": "accepted", "message": "Send prescription OCR text in the 'text' field."}


@router.post("/parse-text")
def parse_text(payload: dict) -> dict:
    return parse_prescription_text(str(payload.get("text", "")))


@router.post("/upload")
async def upload_prescription(file: UploadFile = File(...)) -> dict:
    contents = await file.read()
    return {
        "status": "received",
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "message": (
            "Prescription upload is working. The homepage can run lightweight browser OCR "
            "and send extracted text here for parsing."
        ),
        "next_step": "Use the homepage OCR demo or connect a hosted medical OCR model for stronger handwriting support.",
    }
