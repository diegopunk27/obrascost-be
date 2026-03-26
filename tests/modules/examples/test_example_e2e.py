import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_post_hello_valid(client):
    response = await client.post("/example/hello", json={"name": "TestName"})
    assert response.status_code == 201
    assert response.json() == "Hola TestName!!"


@pytest.mark.asyncio
async def test_post_hello_validation_error(client):
    response = await client.post("/example/hello", json={"name": "Te"})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_post_hello_conflict_single_name(client):
    response = await client.post("/example/hello", json={"name": "Test Name"})
    assert response.status_code == 409
    assert response.json()["message"] == "The name must be a single name"


@pytest.mark.asyncio
async def test_client_with_auth_override(client_with_auth, mock_user):
    """Example of JWT guard override (NestJS TestMockGuard pattern)."""
    assert mock_user.role_name == "ADMIN"
    response = await client_with_auth.get("/health")
    assert response.status_code == 200
