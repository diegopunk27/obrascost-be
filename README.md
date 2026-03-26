# FastAPI CQRS Base (Python)

Boilerplate equivalent to the NestJS CQRS base template: **CQRS buses**, **modular routers**, **JWT auth + permissions**, **global exception handling**, **async PostgreSQL** (SQLModel + asyncpg), **Alembic** migrations, and **pytest + httpx** E2E tests.

## Stack

| Concern        | Technology                          |
|----------------|-------------------------------------|
| API            | FastAPI                             |
| CQRS           | `CommandBus` / `QueryBus` + registry |
| ORM            | SQLModel (SQLAlchemy 2 async)       |
| DB driver      | asyncpg                             |
| Migrations     | Alembic (async env)                 |
| Config         | pydantic-settings (`.env`)          |
| JWT            | python-jose                         |
| Logging        | loguru                              |
| Tests          | pytest, pytest-asyncio, httpx       |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env — set DB_* and JWT_SECRET

# PostgreSQL (Docker)
docker compose -f docker-compose.dev.yml up -d postgres

# Migrations (from project root; loads .env via pydantic-settings)
export PYTHONPATH=src
alembic upgrade head

# Run API
uvicorn main:app --reload --app-dir src --port 4000
```

- OpenAPI: `http://localhost:4000/docs`
- Health: `GET /health`
- Example command: `POST /example/hello` with JSON `{"name": "TestName"}` → `201` and `"Hola TestName!!"`

## Tests

Tests set `TESTING=true` (see `tests/conftest.py`) so the app **does not** open a DB connection — enough for the example CQRS flow.

```bash
export PYTHONPATH=src
pytest tests/ -v
```

For integration tests against a real DB, unset `TESTING`, point `DB_*` to `app_testing`, and run migrations against that database.

## Project layout

```
src/
  app.py              # create_app(), lifespan, buses on app.state
  main.py             # ASGI entry (uvicorn main:app --app-dir src)
  common/             # CQRS, config, DB, auth, exceptions, logging
  modules/            # Feature modules: commands/, queries/, routers/
alembic/              # migrations (async)
tests/                # E2E-style tests with httpx.AsyncClient
```

### CQRS

- **Commands / queries**: Pydantic models under `modules/<feature>/commands|queries/`.
- **Handlers**: async functions registered with `@CommandBus.register(MyCommand)` or `@QueryBus.register(MyQuery)`.
- **Routers**: inject `CommandBus` / `QueryBus` via `Depends(get_command_bus)` / `Depends(get_query_bus)`, then `await bus.execute(dto, db=session)` when the handler needs `AsyncSession` (kwargs are forwarded by parameter name).

### Auth

- `get_current_user` — Bearer JWT (HTTP Bearer).
- `require_permissions("A", "B")` — use as `Depends(require_permissions("A"))` on routes.
- Tests: `app.dependency_overrides[get_current_user] = lambda: mock_user` (same idea as Nest `TestMockGuard`).

### Transactions

- `UnitOfWork` in `common/database/unit_of_work.py` — `async with uow.begin() as session:` or `await uow.with_transaction(handler)`.

## Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

Production compose builds `Dockerfile.prod` (adjust env / orchestration as needed).

## Tooling (Prettier, ESLint, Husky, naming)

El template Nest usa **Prettier + ESLint + Husky** en TypeScript. En este repo:

| Nest / JS        | Aquí |
|------------------|------|
| Prettier (TS/JSON/MD) | **Prettier** para `*.{json,md,yml,yaml,cjs,mjs}`; **Ruff format** para `*.py` (ver `pyproject.toml`) |
| ESLint (`src/` TS)    | **Ruff** lint en `src/` y `tests/`; **ESLint 9** solo en `mcp-servers/**/*.js` (`eslint.config.mjs`) |
| `.eslintrc.js`        | Stub en raíz que ignora todo: el lint real de JS es el flat config (evita que herramientas legacy escaneen Python) |
| `naming-checker.mjs`  | `scripts/naming-checker.mjs` — **snake_case** en `src/` y `tests/` (PEP 8); ver `naming-policies.md` |
| Husky                 | `.husky/pre-commit`: naming + `ruff check/format` (si existe `.venv`) + `lint-staged` |

Setup una vez (requiere **Node.js** + npm):

```bash
npm install          # instala husky, prettier, eslint, lint-staged; ejecuta prepare → husky
npm run mcp:postgresql:install   # dependencias del MCP PostgreSQL
```

## MCP PostgreSQL (Cursor)

Servidor MCP bajo `mcp-servers/postgresql/`, usando las mismas variables `DB_*` que la app.

```bash
npm run mcp:postgresql:install
cp .cursor/mcp.example.json .cursor/mcp.json   # editar credenciales
npm run mcp:postgresql:test
```

Detalle: [mcp-servers/postgresql/docs/README.md](mcp-servers/postgresql/docs/README.md).

## Differences vs NestJS template

- **Validation**: Pydantic returns **422** for body validation (Nest `ValidationPipe` often surfaced as 400).
- **MySQL → PostgreSQL** and **async** driver throughout.
- **No Nest DI**: pass `db=session` (and other deps) explicitly into `bus.execute` when handlers need them.

## Documentation for agents

See [AGENTS.md](AGENTS.md) and [skills/](skills/) for conventions and skill parity with the NestJS template.
