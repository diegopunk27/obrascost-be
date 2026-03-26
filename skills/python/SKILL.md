---
name: python
description: Python style, Pydantic v2, and typing for this API (TypeScript skill equivalent).
---

# Python / Pydantic

## Style

- Python **3.11+**, type hints on public functions and handler signatures.
- **`ruff`** for lint/format (`ruff check src tests`).
- Prefer **explicit** names; avoid `Any` unless justified.

## DTOs

- Request/response bodies: **Pydantic v2** `BaseModel` with `Field(...)` constraints.
- SQLModel models: table models in `common.database` or feature modules; keep API DTOs separate when shapes differ.

## Settings

- Use `get_settings()`; extend `Settings` in `common/config/settings.py` and `.env.example`.

## Imports

- Project root adds `src` to path (`uvicorn --app-dir src`, `PYTHONPATH=src`, or editable install).
- Packages: `common.*`, `modules.*`.
