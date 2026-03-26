# FastAPI CQRS Base — Agent Guidelines

Python/FastAPI counterpart to the NestJS CQRS base template. Use this file plus `skills/` for project-wide patterns.

## Skill mapping (NestJS template → this repo)

| NestJS `skills/` | This repo `skills/` | Notes |
|------------------|---------------------|--------|
| `nestjs-cqrs` | [fastapi-cqrs](skills/fastapi-cqrs/SKILL.md) | CommandBus / QueryBus, handlers, `UnitOfWork` |
| `controllers` | [routers](skills/routers/SKILL.md) | `APIRouter`, OpenAPI, `Depends`, status codes |
| `typescript` | [python](skills/python/SKILL.md) | Pydantic models, typing, `ruff` |
| `testing` | [testing](skills/testing/SKILL.md) | pytest-asyncio, httpx, overrides |
| `code-review` | [code-review](skills/code-review/SKILL.md) | Architecture + security checklist |
| `docs` | [docs](skills/docs/SKILL.md) | README, OpenAPI, docstrings |
| `commit` | [commit](skills/commit/SKILL.md) | Commit message conventions |
| `pr` | [pr](skills/pr/SKILL.md) | PR description template |
| `estimador` | [estimador](skills/estimador/SKILL.md) | Task estimation format |
| `skill-creator` | [skill-creator](skills/skill-creator/SKILL.md) | How to add skills |
| `skill-sync` | [skill-sync](skills/skill-sync/SKILL.md) | Keep AGENTS tables in sync |

## Auto-invoke hints

| When you… | Consult |
|-----------|---------|
| Add a command/query + handler | `fastapi-cqrs` |
| Add HTTP routes / DTOs | `routers`, `python` |
| Add env vars | `code-review` (and `.env.example`) |
| Add migrations | `fastapi-cqrs` + Alembic README section |
| Write or fix tests | `testing` |
| Prepare commit / PR | `commit`, `pr` |

## Architecture (mandatory direction)

- **Writes** go through **commands** + `CommandBus.execute`.
- **Reads** go through **queries** + `QueryBus.execute`.
- **Routers stay thin**: validate with Pydantic, dispatch to the bus, return response models.
- **Business rules** live in handlers (and pure validators), not in routers.
- **Cross-module coupling**: prefer new commands/queries over importing other modules’ internals.

## Configuration

- Never read `os.environ` directly in feature code; use `get_settings()` (`common.config.settings`).
- Every new env var: document in `.env.example`.

## Testing

- Prefer E2E-style tests with `httpx.AsyncClient` for new endpoints.
- Use `TESTING=true` for suites that must not require PostgreSQL (default in `tests/conftest.py`).

---

For detailed patterns, open the linked `SKILL.md` files under `skills/`.
