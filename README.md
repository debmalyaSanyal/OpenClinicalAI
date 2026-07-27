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

## Vercel Deployment

This repository includes a Vercel entrypoint for the lightweight FastAPI API:

```text
api/index.py
```

After importing the GitHub repository in Vercel, keep the project root as the default root directory. Vercel will route requests to the FastAPI app, including:

```text
/docs
/v1/health
```

Heavy OCR/model inference should run in a dedicated backend service or hosted model endpoint, then be called from this API.

## Railway Deployment

This repository can also run as a long-lived Railway backend using:

```text
Procfile
railway.json
```

Deploy from GitHub in Railway, keep the root directory as the repository root, and let Railway use the included start command:

```bash
uvicorn apps.backend.app.main:app --host 0.0.0.0 --port $PORT
```

The Railway public URL will serve the full app at `/` and API endpoints such as `/docs`, `/v1/prescription/analyze`, `/v1/reports`, and `/v1/reasoning/chat`.

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
