# Deployment Guide

Local stack:

```bash
docker compose up
```

Services:

- API
- PostgreSQL
- Neo4j
- Qdrant
- Redis
- Prometheus
- Documentation server

Production deployments should configure:

- external secrets management
- TLS termination
- persistent encrypted volumes
- PHI-safe logging
- RBAC integration
- monitoring and alerting
