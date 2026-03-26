---
name: pr
description: Pull request description template.
---

# Pull requests

## Title

- `#NRO` + short description (max ~10 words).

## Body sections

1. **Motivo de cambio** — problem / goal (2–3 lines).
2. **Cambios realizados** — up to 5 bullets (what, not full implementation detail).
3. **Impacto** — user or system impact (1–2 bullets).
4. **Archivos clave** — up to 5 paths with one line each.
5. **Tareas relacionadas** — `#123`, `#456`.

Use `git --no-pager diff <target-branch>` to summarize.
