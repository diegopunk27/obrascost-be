#!/usr/bin/env bash
# Production start script for Render / similar PaaS.
# Runs alembic migrations + seed (idempotent) + uvicorn.
set -e

export PYTHONPATH=src

echo ">>> Running alembic migrations..."
alembic upgrade head

echo ">>> Seeding database (idempotent)..."
python scripts/seed_dev.py || echo "Seed failed (continuing)"

echo ">>> Starting uvicorn on port ${PORT:-4000}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-4000}" --app-dir src
