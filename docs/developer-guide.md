# Developer Guide

## Setup

```bash
pip install -e ".[dev]"
pytest
```

## Code Style

- Type hints required for public APIs.
- Prefer dependency injection.
- Keep side effects at service edges.
- Keep PHI out of logs.
- Keep medical facts referenced.

## Adding A Module

1. Define a plugin contract or use an existing one.
2. Add tests.
3. Add documentation.
4. Register through configuration, not hardcoding.
5. Ensure FHIR resources are used for clinical data where possible.
