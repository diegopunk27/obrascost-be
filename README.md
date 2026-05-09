# ObrasCost — Backend

API REST de **ObrasCost**, plataforma de gestión y estimación de costos de obras de construcción. Desarrollada con FastAPI + CQRS + PostgreSQL asíncrono.

## Stack

| Concern | Tecnología |
|---|---|
| API | FastAPI |
| Patrón | CQRS (CommandBus / QueryBus) |
| ORM | SQLModel (SQLAlchemy 2 async) |
| DB driver | asyncpg |
| DB | PostgreSQL 16 |
| Migraciones | Alembic (async) |
| Config | pydantic-settings (`.env`) |
| Auth | JWT (python-jose) + bcrypt |
| HTTP cliente | httpx (llamadas a api-multiagente) |
| Logging | loguru |
| Tests | pytest + pytest-asyncio |
| Linting | Ruff (check + format) |

## Inicio rápido

### 1. Levantar la base de datos (Docker)

```bash
docker compose -f docker-compose.db.yml up -d
```

Esto inicia solo PostgreSQL en `localhost:5432`. La app corre desde el host.

### 2. Instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Editar .env — ajustar DB_* y JWT_SECRET si es necesario
```

### 3. Migraciones + seed

```bash
export PYTHONPATH=src
alembic upgrade head
python scripts/seed_dev.py   # 1 usuario admin + 10 rubros estándar
```

### 4. Ejecutar la API

```bash
uvicorn main:app --reload --app-dir src --port 4000
```

- Swagger: `http://localhost:4000/docs`
- Health: `GET /health`

### Credenciales del seed

| Campo | Valor |
|---|---|
| Email | `admin@obrascost.com` |
| Contraseña | `admin123` |

## Módulos de dominio

| Módulo | Entidades | Endpoints |
|---|---|---|
| `auth/` | Usuario (email, password_hash, nombre, role) | `POST /auth/login`, `GET /auth/me` |
| `rubros/` | Rubro (nombre, descripcion, costo_referencia_m2) | CRUD `/rubros` |
| `obras/` | Obra (superficie_m2, provincia_id, presupuesto_inicial, estado) | CRUD `/obras` + `POST /obras/{id}/estimacion` |
| `gastos/` | Gasto (obra_id, rubro_id, monto, fecha) | CRUD `/obras/{id}/gastos` |

### Endpoint de estimación

```
POST /obras/{id}/estimacion?con_ia=false   # heurística pura
POST /obras/{id}/estimacion?con_ia=true    # heurística + análisis LLM
```

**Respuesta:**
```json
{
  "total_estimado": 3000000,
  "desglose_por_rubro": { "Estructura": 2000000, "Pintura": 500000 },
  "margen_error_pct": 15,
  "fuente": "ia",
  "sugerencia_ia": "Considerar aumento en terminaciones.",
  "ajuste_recomendado_pct": 5,
  "alertas": []
}
```

## Testing

### Unitarios

```bash
export PYTHONPATH=src
pytest tests/ -v
```

**Cobertura:** ≥ 83% global (76 tests). El flag `TESTING=true` desactiva la conexión real a BD — apropiado para tests unitarios de handlers CQRS.

```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
# Reporte HTML en htmlcov/
```

### Qué se testea

| Módulo | Tests |
|---|---|
| `auth/` | Login command, validaciones, JWT |
| `rubros/` | CRUD commands y queries |
| `obras/` | CRUD commands y queries |
| `gastos/` | CRUD commands y queries |
| `estimacion/` | `heuristic_estimator` con pytest.parametrize (superficies edge, rubros vacíos, factores regionales); `ai_estimator_client` con respx (timeouts, 500, JSON inválido) |

## CI/CD (GitHub Actions)

Workflow: [`.github/workflows/be-ci.yml`](.github/workflows/be-ci.yml)

| Job | Qué hace |
|---|---|
| `lint` | `ruff check src tests` + `ruff format --check` |
| `test` | `pytest --cov=src --cov-fail-under=80` — sube artefacto `coverage-be` |

**Triggers:** push y PR a `main` / `development`.

## Estructura del proyecto

```
src/
  app.py                  create_app(), lifespan, buses en app.state
  main.py                 Entry point ASGI
  common/                 CQRS, config, DB, auth, excepciones, logging
  modules/
    auth/                 Login + JWT + usuario actual
    rubros/               Catálogo de rubros de construcción
    obras/
      estimacion/         heuristic_estimator.py + ai_estimator_client.py
    gastos/
alembic/                  Migraciones async
scripts/
  seed_dev.py             Datos iniciales (admin + 10 rubros)
tests/
  modules/                Tests unitarios por módulo
```

## Migraciones

| Revisión | Descripción |
|---|---|
| `0001` | Tablas base (provincias, ejemplos) |
| `0002` | usuarios + rubros |
| `0003` | obras (FK usuarios, provincias) |
| `0004` | gastos (FK obras, rubros) |

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `DB_HOST` | `localhost` | Host PostgreSQL |
| `DB_PORT` | `5432` | Puerto |
| `DB_USERNAME` | `postgres` | Usuario |
| `DB_PASSWORD` | `postgres` | Contraseña |
| `DB_DATABASE` | `app_dev` | Nombre de la BD |
| `JWT_SECRET` | — | Clave secreta para firmar tokens |
| `AI_API_BASE_URL` | `http://localhost:8080` | URL del api-multiagente |
| `TESTING` | `false` | `true` desactiva la conexión real a BD |
