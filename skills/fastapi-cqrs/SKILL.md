---
name: fastapi-cqrs
description: CQRS with CommandBus and QueryBus in this FastAPI template.
---

# FastAPI CQRS

## Commands & queries

- **Command**: Pydantic `BaseModel` in `modules/<feature>/commands/...`.
- **Query**: same under `modules/<feature>/queries/...`.
- **One handler** per message type.

## Handlers

Register async callables:

```python
from common.cqrs.command_bus import CommandBus

@CommandBus.register(MyCommand)
async def handle_my_command(command: MyCommand, db: AsyncSession) -> MyResponse:
    ...
```

`CommandBus.execute(command, db=session)` forwards only kwargs that appear in the handler signature.

## Router

```python
@router.post("", status_code=201)
async def create(
    body: MyCommand,
    bus: CommandBus = Depends(get_command_bus),
    session: AsyncSession = Depends(get_session),
):
    return await bus.execute(body, db=session)
```

## Transactions

Use `UnitOfWork` (`common.database.unit_of_work`) for multi-step writes.

## Migrations

- Import all SQLModel tables in `alembic/env.py` so autogenerate sees metadata.
- Run: `PYTHONPATH=src alembic revision --autogenerate -m "msg"` then `alembic upgrade head`.

## Module layout

```
modules/<name>/
  commands/
  queries/
  routers/
  repositories/   # optional
  validators/     # optional pure functions
```
