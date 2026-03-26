#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('Configuring MCP server for PostgreSQL (FastAPI CQRS base)...');

const serverFile = path.join(__dirname, '..', 'src', 'mcp-postgres-server.js');
if (!fs.existsSync(serverFile)) {
  console.log('Error: mcp-postgres-server.js not found.');
  process.exit(1);
}

console.log('MCP server file found.');

const nodeModulesDir = path.join(__dirname, '..', '..', 'node_modules');
if (!fs.existsSync(nodeModulesDir)) {
  console.log('Error: run `npm install` inside mcp-servers/ first.');
  process.exit(1);
}

console.log('Dependencies OK.');
console.log('');
console.log('Next steps:');
console.log('1. Copy .cursor/mcp.example.json to .cursor/mcp.json and set DB_* (match .env).');
console.log('2. Ensure PostgreSQL is running (e.g. docker compose -f docker-compose.dev.yml up -d postgres).');
console.log('3. Restart Cursor.');
console.log('');
console.log('Test: npm run mcp:postgresql:test (from repo root) or npm run postgresql:test --prefix mcp-servers');
console.log('');
