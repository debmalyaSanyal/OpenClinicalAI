from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field


SUPPORTED_RESOURCE_TYPES = {
    "Patient",
    "Practitioner",
    "Organization",
    "Encounter",
    "Medication",
    "MedicationRequest",
    "MedicationStatement",
    "Observation",
    "Condition",
    "AllergyIntolerance",
    "DiagnosticReport",
    "DocumentReference",
    "CarePlan",
    "Procedure",
    "Appointment",
    "ImagingStudy",
    "Bundle",
}


class FHIRResource(BaseModel):
    resourceType: str
    id: str | None = None
    meta: dict[str, Any] | None = None
    extension: list[dict[str, Any]] | None = None
    contained: list[dict[str, Any]] | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    supported_resource_types: ClassVar[set[str]] = SUPPORTED_RESOURCE_TYPES

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FHIRResource":
        known = {k: data.get(k) for k in ["resourceType", "id", "meta", "extension", "contained"] if k in data}
        payload = {k: v for k, v in data.items() if k not in known}
        return cls(**known, payload=payload)

    def to_fhir_json(self) -> dict[str, Any]:
        base = self.model_dump(exclude={"payload", "supported_resource_types"}, exclude_none=True)
        base.update(self.payload)
        return base
