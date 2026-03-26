#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Testing PostgreSQL MCP server connection...');

const serverFile = path.join(__dirname, '..', 'src', 'mcp-postgres-server.js');
if (!fs.existsSync(serverFile)) {
  console.log('Error: MCP server file not found.');
  process.exit(1);
}

const nodeModulesDir = path.join(__dirname, '..', '..', 'node_modules');
if (!fs.existsSync(nodeModulesDir)) {
  console.log('Error: run npm install in mcp-servers/ first.');
  process.exit(1);
}

console.log('Optional: pg_isready on localhost:5432...');
try {
  execSync('pg_isready -h localhost -p 5432', { stdio: 'pipe' });
  console.log('PostgreSQL responds on localhost:5432');
} catch {
  console.log('pg_isready not available or DB not ready; continuing...');
}

let env = { ...process.env };
const repoRoot = path.join(__dirname, '..', '..', '..');
const mcpConfigPath = path.join(repoRoot, '.cursor', 'mcp.json');

try {
  if (fs.existsSync(mcpConfigPath)) {
    const configRaw = fs.readFileSync(mcpConfigPath, 'utf8');
    const config = JSON.parse(configRaw);
    const pgEnv =
      config?.mcpServers?.postgres?.env ??
      config?.mcpServers?.postgresql?.env ??
      {};
    env = { ...env, ...pgEnv };
    console.log('Loaded DB_* from .cursor/mcp.json');
  } else {
    console.log('No .cursor/mcp.json — using process env / .env if loaded by dotenv in server.');
  }
} catch (e) {
  console.log('Could not read .cursor/mcp.json:', e.message);
}

const serverProcess = spawn('node', [serverFile], {
  env,
  stdio: ['pipe', 'pipe', 'pipe'],
});

let output = '';
let errorOutput = '';

serverProcess.stdout.on('data', (data) => {
  output += data.toString();
});

serverProcess.stderr.on('data', (data) => {
  errorOutput += data.toString();
});

setTimeout(() => {
  serverProcess.kill();
}, 10000);

serverProcess.on('close', () => {
  const combined = output + errorOutput;
  if (combined.includes('Connected to PostgreSQL database')) {
    console.log('Success: MCP server connected to PostgreSQL.');
    process.exit(0);
  }
  console.log('Connection check failed. Is PostgreSQL up and DB_* correct?');
  console.log('--- stdout ---\n', output);
  console.log('--- stderr ---\n', errorOutput);
  process.exit(1);
});
