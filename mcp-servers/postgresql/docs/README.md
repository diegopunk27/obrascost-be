# MCP server (PostgreSQL)

Conecta Cursor (u otro cliente MCP) a la misma base **PostgreSQL** que usa la API (`DB_*` en `.env`).

## Instalación

Desde la raíz del repo:

```bash
npm run mcp:postgresql:install
# o: cd mcp-servers && npm install
```

## Configuración en Cursor

1. Copia la plantilla y ajusta credenciales (alineadas con `.env.example`):

   ```bash
   mkdir -p .cursor && cp .cursor/mcp.example.json .cursor/mcp.json
   ```

2. Edita `.cursor/mcp.json` con tu `DB_PASSWORD` y, si aplica, `DB_DATABASE`.

3. **No subas** `.cursor/mcp.json` al repositorio (está en `.gitignore`).

4. Reinicia Cursor.

## Comprobar conexión

```bash
npm run mcp:postgresql:setup
npm run mcp:postgresql:test
```

El script de prueba lee `DB_*` desde `.cursor/mcp.json` si existe.

## Herramientas

| Herramienta       | Descripción                          |
|-------------------|--------------------------------------|
| `query_database`  | Ejecuta SQL (con parámetros opcionales) |
| `list_tables`     | Tablas en el esquema `public`        |
| `describe_table`  | Columnas de una tabla                |
| `get_table_data`  | Muestra filas (LIMIT)                |

## Seguridad

- Usa un usuario de solo lectura si solo necesitas inspección.
- Las credenciales van en variables de entorno / `mcp.json` local, nunca en el código.
