# OpenClinicalAI

OpenClinicalAI is a modular, FHIR-first, open-source clinical AI platform foundation.

It is not a chatbot, not just OCR, and not a single AI model. It is the infrastructure that future clinical AI modules plug into: OCR, parsing, medical knowledge, reasoning, safety guardrails, reports, hospital integrations, and patient education workflows.

## Principles

- FHIR-first clinical data model
- API-first services
- Plugin-based extension points
- Configurable model registry
- Secure by default
- PHI-safe logging by default
- Dockerized local stack
- Testable and modular architecture

## Quick Start

```bash
cp .env.example .env
docker compose up
```

API docs are available at:

```text
http://localhost:8000/docs
```

Project documentation can be published with GitHub Pages using the included `pages.yml` workflow.

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
uvicorn apps.backend.app.main:app --reload
```

## Project Layout

```text
apps/
core/
plugins/
datasets/
training/
models/
evaluation/
examples/
tests/
docker/
deployment/
monitoring/
docs/
.github/
scripts/
```

## Status

This repository is a foundation for community development. It intentionally avoids fake AI outputs and hardcoded medical facts. Clinical modules should add evidence-backed data, tests, safety validation, and references.
