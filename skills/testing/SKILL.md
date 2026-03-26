---
name: testing
description: pytest, pytest-asyncio, httpx E2E patterns for this app.
---

# Testing

## Layout

- `tests/conftest.py` — shared fixtures (`client`, `app`, auth overrides).
- Mirror `src/modules/...` under `tests/modules/...` when possible.

## E2E with httpx

```python
@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

## Auth mocking

```python
app.dependency_overrides[get_current_user] = lambda: mock_user
```

Clear overrides after tests (`app.dependency_overrides.clear()` in fixture teardown).

## Environment

- `TESTING=true` skips DB engine startup (see `Settings.testing` + `app` lifespan).

## Run

```bash
PYTHONPATH=src pytest tests/ -v
```
