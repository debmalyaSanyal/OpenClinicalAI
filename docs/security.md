# Security

Security defaults:

- No secrets in source code.
- PHI redaction in logs by default.
- RBAC hooks available in `core.security`.
- Input validation for FHIR resources.
- Audit hashing helper.
- Prompt-injection controls should be added to AI plugins.

Never log sensitive health information by default. Set `OPENCLINICALAI_LOG_PHI=true` only in controlled local debugging environments.
