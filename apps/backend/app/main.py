from __future__ import annotations

from fastapi import FastAPI

from apps.backend.app.api.v1 import fhir, health, knowledge, patient, prescription, reasoning, reports, safety, search
from core.config import Settings
from core.observability.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings)
    app = FastAPI(
        title="OpenClinicalAI API",
        version=settings.api_version,
        description="FHIR-first modular clinical AI platform API.",
    )
    app.include_router(health.router, prefix="/v1", tags=["health"])
    app.include_router(prescription.router, prefix="/v1/prescription", tags=["prescription"])
    app.include_router(fhir.router, prefix="/v1/fhir", tags=["fhir"])
    app.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
    app.include_router(knowledge.router, prefix="/v1/knowledge", tags=["knowledge"])
    app.include_router(reasoning.router, prefix="/v1/reasoning", tags=["reasoning"])
    app.include_router(safety.router, prefix="/v1/safety", tags=["safety"])
    app.include_router(patient.router, prefix="/v1/patient", tags=["patient"])
    app.include_router(search.router, prefix="/v1/search", tags=["search"])
    return app


app = create_app()
