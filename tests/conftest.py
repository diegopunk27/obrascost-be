import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from common.auth.dependencies import get_current_user
from common.auth.schemas import UserSchema
from common.config.settings import get_settings


@pytest.fixture(scope="session", autouse=True)
def _test_env() -> None:
    """Mirror NestJS `.env.testing`: no real DB required for example E2E."""
    os.environ.setdefault("TESTING", "true")
    os.environ.setdefault("JWT_SECRET", "test_jwt_secret")
    os.environ.setdefault("JWT_ISSUER", "test_app")
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def app():
    from app import create_app

    return create_app()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user() -> UserSchema:
    return UserSchema(
        id=1,
        email="admin@example.com",
        role_id=1,
        role_name="ADMIN",
        permissions=["READ_DATA", "WRITE_DATA"],
    )


@pytest_asyncio.fixture
async def client_with_auth(app, mock_user: UserSchema) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: mock_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
