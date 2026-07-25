from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.fhir.bundle import FHIRBundle
from core.fhir.resources import FHIRResource
from core.fhir.validation import FHIRValidationError, validate_resource

router = APIRouter()


@router.post("/validate")
def validate(payload: dict) -> dict:
    try:
        validate_resource(payload)
    except FHIRValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"valid": True, "resourceType": payload["resourceType"]}


@router.post("/bundle")
def bundle(resources: list[dict]) -> dict:
    typed = [FHIRResource.from_dict(item) for item in resources]
    return FHIRBundle.from_resources(typed).model_dump(exclude_none=True)
