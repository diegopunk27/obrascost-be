"""E2E fixtures: real PostgreSQL + alembic migrations + clean state per test.

Strategy:
  - session scope: ensure TESTING=false, run `alembic upgrade head` once, seed admin + rubros
  - function scope: TRUNCATE obras + gastos at the start of each test (keep usuarios + rubros)

Override the parent conftest's `TESTING=true` by setting the env BEFORE collection.
"""

import os

# Must run before parent conftest's setdefault — force real DB mode for e2e
os.environ["TESTING"] = "false"
os.environ.setdefault("JWT_SECRET", "ci-test-secret-key-obrascost")
os.environ.setdefault("JWT_ISSUER", "obrascost-e2e")

import subprocess  # noqa: E402
import sys  # noqa: E402
from collections.abc import AsyncIterator  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def _migrate_and_seed() -> None:
    """Run alembic migrations once per test session, then seed admin + rubros."""
    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")}
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "seed_dev.py")],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Build app + open lifespan + clean dynamic tables before yielding the client."""
    from common.config.settings import get_settings

    get_settings.cache_clear()
    from app import create_app
    from common.database.session import get_engine

    app = create_app()
    async with app.router.lifespan_context(app):
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE gastos, obras RESTART IDENTITY CASCADE"))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Login as the seeded admin and return Authorization headers."""
    response = await client.post(
        "/auth/login",
        json={"email": "admin@obrascost.ar", "password": "Admin1234!"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
