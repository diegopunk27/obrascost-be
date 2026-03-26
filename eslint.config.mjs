/**
 * ESLint flat config for Node ESM in `mcp-servers/` (Python project: Ruff owns `src/`).
 */
import js from '@eslint/js';
import globals from 'globals';

export default [
  {
    ignores: ['**/node_modules/**', '.venv/**'],
  },
  {
    files: ['mcp-servers/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: globals.node,
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-console': 'off',
    },
  },
];
