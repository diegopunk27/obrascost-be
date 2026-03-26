---
name: routers
description: FastAPI routers, OpenAPI, and HTTP conventions (Nest controllers equivalent).
---

# Routers (Controllers)

## Rules

- **Thin routes**: parse/validate body with Pydantic → `bus.execute` → return result.
- Use **meaningful** `tags`, `summary`, and `response_model` for OpenAPI.
- Set **`status_code`** explicitly when not `200` (e.g. `201` for creates).

## Auth

```python
from common.auth.dependencies import get_current_user, require_permissions
from common.auth.schemas import UserSchema

@router.get("/me")
async def me(user: UserSchema = Depends(get_current_user)):
    ...

@router.get("/admin")
async def admin(user: UserSchema = Depends(require_permissions("ADMIN_ACTION"))):
    ...
```

## CQRS

- POST/PUT/PATCH/DELETE → command bus.
- GET → query bus.

## Errors

- Raise domain types: `ConflictError`, `NotFoundError`, `UnprocessableDomainError` from `common.exceptions`.
- Or `HTTPException` for simple cases; global handlers normalize responses where possible.
