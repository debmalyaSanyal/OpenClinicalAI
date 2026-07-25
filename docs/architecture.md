# Architecture

OpenClinicalAI uses clean architecture boundaries:

- `apps/`: deployable applications and APIs.
- `core/`: shared platform primitives such as FHIR, plugins, model registry, config, security, and observability.
- `plugins/`: extension packages that register capabilities.
- `models/`: model registry and model configuration.
- `datasets/`, `training/`, `evaluation/`: reproducible AI workflows.
- `deployment/`, `docker/`, `monitoring/`: operational tooling.

Services are intended to be independently deployable. Shared behavior should live in `core`, while domain-specific logic should be behind plugin contracts.
