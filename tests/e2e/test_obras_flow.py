"""E2E flujo completo de obras: crear → listar → obtener → actualizar → estimar → eliminar."""

import pytest
from httpx import AsyncClient


def _payload_obra(nombre: str = "Casa de prueba") -> dict:
    return {
        "nombre": nombre,
        "direccion": "Av. Siempreviva 742",
        "provincia_id": None,
        "superficie_m2": 120.0,
        "fecha_inicio": "2026-01-15",
        "fecha_fin_estimada": "2026-12-31",
        "estado": "borrador",
        "presupuesto_inicial": 5000000.0,
    }


@pytest.mark.asyncio
async def test_crear_obra_devuelve_201_y_id(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/obras", json=_payload_obra(), headers=auth_headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["id"] > 0
    assert body["nombre"] == "Casa de prueba"
    assert body["superficie_m2"] == 120.0


@pytest.mark.asyncio
async def test_listar_obras_devuelve_solo_las_creadas(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    await client.post("/obras", json=_payload_obra("Obra A"), headers=auth_headers)
    await client.post("/obras", json=_payload_obra("Obra B"), headers=auth_headers)

    response = await client.get("/obras", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    nombres = {o["nombre"] for o in body}
    assert nombres == {"Obra A", "Obra B"}


@pytest.mark.asyncio
async def test_obtener_obra_por_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create_resp = await client.post("/obras", json=_payload_obra(), headers=auth_headers)
    obra_id = create_resp.json()["id"]

    response = await client.get(f"/obras/{obra_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == obra_id


@pytest.mark.asyncio
async def test_actualizar_obra_modifica_campos(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    create_resp = await client.post("/obras", json=_payload_obra(), headers=auth_headers)
    obra_id = create_resp.json()["id"]

    response = await client.patch(
        f"/obras/{obra_id}",
        json={"estado": "en_progreso", "presupuesto_inicial": 7500000.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["estado"] == "en_progreso"
    assert body["presupuesto_inicial"] == 7500000.0


@pytest.mark.asyncio
async def test_eliminar_obra_devuelve_204(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    create_resp = await client.post("/obras", json=_payload_obra(), headers=auth_headers)
    obra_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/obras/{obra_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/obras/{obra_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_estimar_obra_sin_ia_devuelve_total(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    create_resp = await client.post("/obras", json=_payload_obra(), headers=auth_headers)
    obra_id = create_resp.json()["id"]

    response = await client.post(f"/obras/{obra_id}/estimacion?con_ia=false", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_estimado"] > 0
    assert body["fuente"] == "heuristica"
    # 10 rubros del seed → 10 entradas en el desglose
    assert len(body["desglose_por_rubro"]) == 10
    assert body["margen_error_pct"] > 0


@pytest.mark.asyncio
async def test_validacion_superficie_negativa_devuelve_422(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    payload = _payload_obra()
    payload["superficie_m2"] = -50.0
    response = await client.post("/obras", json=payload, headers=auth_headers)
    assert response.status_code == 422
