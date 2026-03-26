#!/usr/bin/env node
/**
 * Naming checker for Python layout: snake_case dirs and .py modules under src/ and tests/.
 * (Nest template used kebab-case for TS files; Python uses PEP 8 snake_case.)
 */
import fs from 'fs';
import path from 'path';

const SCAN_ROOTS = ['./src', './tests'];

const SKIP_DIR_NAMES = new Set([
  '__pycache__',
  '.venv',
  'venv',
  'node_modules',
  '.git',
  '.ruff_cache',
  '.pytest_cache',
  'egg-info',
  '.idea',
  '.vscode',
]);

const DIR_PATTERN = /^[a-z][a-z0-9_]*$/;
const PY_MODULE_PATTERN = /^[a-z][a-z0-9_]*$/;

function shouldSkipDir(relPath, name) {
  if (SKIP_DIR_NAMES.has(name)) return true;
  if (name.endsWith('.egg-info')) return true;
  if (relPath.includes(`${path.sep}alembic${path.sep}versions`)) return true;
  return false;
}

function checkNamingConvention(rootDir) {
  if (!fs.existsSync(rootDir)) {
    return;
  }

  function walk(dir, relBase) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const rel = relBase ? path.join(relBase, entry.name) : entry.name;

      if (entry.isDirectory()) {
        if (shouldSkipDir(rel, entry.name)) continue;

        if (!DIR_PATTERN.test(entry.name)) {
          console.log(
            `La carpeta no respeta snake_case (minúsculas, números, guión bajo): ${rel}`,
          );
          process.exit(1);
        }
        walk(fullPath, rel);
        continue;
      }

      if (rel.includes(`${path.sep}alembic${path.sep}versions${path.sep}`)) continue;

      const ext = path.extname(entry.name);
      if (ext !== '.py') continue;

      const base = path.basename(entry.name, ext);
      if (base === '__init__') continue;

      if (!PY_MODULE_PATTERN.test(base)) {
        console.log(`El módulo .py no respeta snake_case: ${rel}`);
        process.exit(1);
      }
    }
  }

  walk(rootDir, '');
}

for (const root of SCAN_ROOTS) {
  checkNamingConvention(root);
}

console.log('Naming check OK (src/, tests/).');
