"""E2E auth flow: login + /auth/me + protección de rutas."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_admin_devuelve_token(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "admin@obrascost.ar", "password": "Admin1234!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_credenciales_invalidas_devuelve_401(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "admin@obrascost.ar", "password": "wrong-password"},
    )
    assert response.status_code in (401, 404)


@pytest.mark.asyncio
async def test_me_con_token_valido_devuelve_usuario(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@obrascost.ar"


@pytest.mark.asyncio
async def test_me_sin_token_devuelve_401(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_obras_sin_token_es_rechazado(client: AsyncClient) -> None:
    response = await client.get("/obras")
    assert response.status_code in (401, 403)
