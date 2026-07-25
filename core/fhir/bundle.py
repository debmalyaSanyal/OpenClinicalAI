from __future__ import annotations

from pydantic import BaseModel, Field

from core.fhir.resources import FHIRResource


class FHIRBundle(BaseModel):
    resourceType: str = "Bundle"
    type: str = "collection"
    entry: list[dict] = Field(default_factory=list)

    @classmethod
    def from_resources(cls, resources: list[FHIRResource]) -> "FHIRBundle":
        return cls(entry=[{"resource": resource.to_fhir_json()} for resource in resources])
