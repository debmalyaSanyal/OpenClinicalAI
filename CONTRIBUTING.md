# Contributing

Thank you for contributing to OpenClinicalAI.

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Standards

- Keep modules independently testable.
- Prefer FHIR resources for clinical data.
- Do not hardcode models.
- Do not commit secrets, private datasets, or PHI.
- Add references for medical knowledge.
- Keep safety behavior conservative.

## Commit Guidance

Use semantic commit prefixes such as:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `security:`
