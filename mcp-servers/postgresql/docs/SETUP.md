# MCP PostgreSQL — setup rápido

```bash
npm run mcp:postgresql:install
cp .cursor/mcp.example.json .cursor/mcp.json   # editar DB_*
npm run mcp:postgresql:setup
npm run mcp:postgresql:test
```

Reinicia Cursor tras crear o cambiar `mcp.json`.

Estructura:

```
mcp-servers/
  postgresql/
    src/mcp-postgres-server.js
    scripts/{setup.cjs,test.cjs}
```

Variables: mismos nombres que en `.env.example` (`DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DATABASE`).
