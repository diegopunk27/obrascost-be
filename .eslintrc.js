/**
 * NestJS template used `.eslintrc.js` for TypeScript in `src/`.
 *
 * This Python repo uses **Ruff** for `src/` and **ESLint 9 flat config** for Node code under
 * `mcp-servers/`. See `eslint.config.mjs`. Configure your editor for flat config if needed
 * (e.g. VS Code: `eslint.useFlatConfig`: true).
 *
 * This stub keeps root-level ESLint from scanning the whole tree when a tool still invokes
 * the legacy config entrypoint.
 */
module.exports = {
  root: true,
  ignorePatterns: ['**/*'],
};
