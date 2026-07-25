# API Reference

The FastAPI service automatically generates OpenAPI documentation at `/docs`.

Versioned endpoints:

- `/v1/health`
- `/v1/prescription`
- `/v1/fhir`
- `/v1/reports`
- `/v1/knowledge`
- `/v1/reasoning`
- `/v1/safety`
- `/v1/patient`
- `/v1/search`

Endpoint implementations are intentionally plugin-backed. Core platform endpoints validate contracts and route to configured modules.
