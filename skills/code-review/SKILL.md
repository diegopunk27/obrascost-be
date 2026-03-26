---
name: code-review
description: Architecture and review checklist for FastAPI CQRS codebase.
---

# Code review

## Checklist

- [ ] Router only dispatches CQRS; no business rules in route functions.
- [ ] New env vars in `.env.example` and `Settings`.
- [ ] DB access in handlers/repos, not routers.
- [ ] Migrations for schema changes (Alembic).
- [ ] Tests for new endpoints (httpx + status/body assertions).
- [ ] JWT secrets not hardcoded; permissions enforced where required.
- [ ] Exceptions: domain errors vs generic 500; no leaking stack traces in responses.

## CQRS boundaries

- Prefer **commands/queries** between modules instead of deep service imports.
- Keep validators **pure** (no DB); load data in handler then validate.
