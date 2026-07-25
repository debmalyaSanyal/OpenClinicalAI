from __future__ import annotations

from core.fhir.resources import SUPPORTED_RESOURCE_TYPES


class FHIRValidationError(ValueError):
    pass


def validate_resource(resource: dict) -> None:
    resource_type = resource.get("resourceType")
    if not resource_type:
        raise FHIRValidationError("FHIR resource must include resourceType.")
    if resource_type not in SUPPORTED_RESOURCE_TYPES:
        raise FHIRValidationError(f"Unsupported FHIR resourceType: {resource_type}.")
    if "id" in resource and not isinstance(resource["id"], str):
        raise FHIRValidationError("FHIR id must be a string when present.")
