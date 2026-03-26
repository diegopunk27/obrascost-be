# Nomenclatura del proyecto (Python)

Paridad de intención con el template NestJS; convenciones alineadas con **PEP 8** y este repo.

## Archivos y carpetas (Python)

- **Carpetas** bajo `src/` y `tests/`: **snake_case** en minúsculas (`commands`, `hello`, `example_router` como nombre de archivo va con guiones bajos en `.py`).
- **Módulos `.py`**: **snake_case** (`hello_command.py`, `example_router.py`).
- **`__init__.py`**: permitido explícitamente.
- **Alembic**: la carpeta `alembic/versions/` está **excluida** del checker (revisiones con prefijos numéricos).

## Endpoints (HTTP)

- Recursos en **plural** donde aplique; estilo REST coherente con OpenAPI (`/example/hello` como demo).

## Clases / modelos Pydantic / SQLModel

- **PascalCase** (`HelloCommand`, `UserSchema`, `MasterModel`).

## Funciones y métodos

- **snake_case** (`get_settings`, `handle_hello`).

## Variables y atributos

- **snake_case** (`user_id`, `command_bus`).

## Constantes

- **MAYÚSCULAS_CON_GUIONES_BAJOS** (`MAX_RETRIES`, `DEFAULT_LIMIT`).

## JavaScript (solo `mcp-servers/`)

- Archivos **kebab-case** o **lower** al estilo del SDK MCP (`mcp-postgres-server.js`).

El script `npm run check:naming` valida `src/` y `tests/` con reglas Python anteriores.
