import json

import pytest
import respx
from httpx import Response

from modules.obras.estimacion.ai_estimator_client import _parse_json_block, enriquecer_con_ia
from modules.obras.estimacion.heuristic_estimator import EstimacionHeuristica

AI_URL = "http://localhost:8080/estimacion-obra"

BASE_ESTIMACION = EstimacionHeuristica(
    total_estimado=5_000_000.0,
    desglose_por_rubro={"Estructura": 3_000_000.0, "Terminaciones": 2_000_000.0},
    margen_error_pct=15.0,
)


class TestParseJsonBlock:
    def test_extrae_json_limpio(self):
        text = '{"sugerencia_narrativa": "OK", "ajuste_recomendado_pct": 5, "alertas": []}'
        result = _parse_json_block(text)
        assert result["ajuste_recomendado_pct"] == 5

    def test_extrae_json_con_texto_previo(self):
        text = 'Aquí va mi análisis:\n{"key": "value"}\n\nFin.'
        result = _parse_json_block(text)
        assert result["key"] == "value"

    def test_retorna_vacio_si_no_hay_json(self):
        assert _parse_json_block("Sin JSON aquí") == {}

    def test_retorna_vacio_si_json_invalido(self):
        assert _parse_json_block("{clave: valor}") == {}


class TestEnriquecerConIa:
    @respx.mock
    @pytest.mark.asyncio
    async def test_respuesta_correcta_retorna_sugerencia(self):
        payload = {
            "sugerencia_narrativa": "La obra requiere atención en los acabados.",
            "ajuste_recomendado_pct": 8.0,
            "alertas": ["Revisar precios de materiales"],
        }
        respx.post(AI_URL).mock(return_value=Response(200, json=payload))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia == "La obra requiere atención en los acabados."
        assert ajuste == 8.0
        assert alertas == ["Revisar precios de materiales"]

    @respx.mock
    @pytest.mark.asyncio
    async def test_respuesta_sin_sugerencia_retorna_none(self):
        respx.post(AI_URL).mock(return_value=Response(200, json={"alertas": []}))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia is None
        assert ajuste is None

    @respx.mock
    @pytest.mark.asyncio
    async def test_502_reintenta_y_eventualmente_succeed(self, monkeypatch):
        # Acelera los sleeps del retry para que el test sea rápido
        import modules.obras.estimacion.ai_estimator_client as mod

        async def _fast_sleep(_seconds):
            return None

        monkeypatch.setattr(mod.asyncio, "sleep", _fast_sleep)

        success_payload = {
            "sugerencia_narrativa": "OK tras retry",
            "ajuste_recomendado_pct": 3.0,
            "alertas": [],
        }
        route = respx.post(AI_URL).mock(
            side_effect=[
                Response(502, text="Bad Gateway"),
                Response(503, text="Service Unavailable"),
                Response(200, json=success_payload),
            ]
        )

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert route.call_count == 3
        assert sugerencia == "OK tras retry"
        assert ajuste == 3.0
        assert alertas == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_502_persistente_degrada_con_alerta(self, monkeypatch):
        import modules.obras.estimacion.ai_estimator_client as mod

        async def _fast_sleep(_seconds):
            return None

        monkeypatch.setattr(mod.asyncio, "sleep", _fast_sleep)

        route = respx.post(AI_URL).mock(return_value=Response(502, text="Bad Gateway"))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert route.call_count == 3
        assert sugerencia is None
        assert ajuste is None
        assert len(alertas) == 1
        assert "no está disponible" in alertas[0]

    @respx.mock
    @pytest.mark.asyncio
    async def test_error_500_degrada_con_alerta(self):
        respx.post(AI_URL).mock(return_value=Response(500, text="Internal Server Error"))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=None,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia is None
        assert ajuste is None
        assert len(alertas) == 1
        assert "no está disponible" in alertas[0]

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_degrada_con_alerta_visible(self, monkeypatch):
        import httpx

        respx.post(AI_URL).mock(side_effect=httpx.TimeoutException("timeout"))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia is None
        assert ajuste is None
        assert len(alertas) == 1
        assert "tardó demasiado" in alertas[0]
        assert "arranque en frío" in alertas[0]

    @respx.mock
    @pytest.mark.asyncio
    async def test_json_invalido_degrada_con_alerta(self):
        respx.post(AI_URL).mock(return_value=Response(200, text="not json at all"))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia is None
        assert ajuste is None
        assert len(alertas) == 1
        assert "no está disponible" in alertas[0]

    @respx.mock
    @pytest.mark.asyncio
    async def test_campo_sugerencia_alternativo(self):
        payload = {"sugerencia": "Alternativa OK", "ajuste_recomendado_pct": None, "alertas": []}
        respx.post(AI_URL).mock(return_value=Response(200, json=payload))

        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra="Casa Test",
            superficie_m2=100,
            provincia_id=1,
            estimacion_base=BASE_ESTIMACION,
        )

        assert sugerencia == "Alternativa OK"
        assert ajuste is None

    @respx.mock
    @pytest.mark.asyncio
    async def test_payload_enviado_contiene_datos_obra(self):
        payload = {"sugerencia_narrativa": "OK", "ajuste_recomendado_pct": 0, "alertas": []}
        route = respx.post(AI_URL).mock(return_value=Response(200, json=payload))

        await enriquecer_con_ia(
            nombre_obra="Obra García",
            superficie_m2=150,
            provincia_id=2,
            estimacion_base=BASE_ESTIMACION,
        )

        sent = json.loads(route.calls[0].request.content)
        assert sent["nombre_obra"] == "Obra García"
        assert sent["superficie_m2"] == 150
        assert sent["provincia_id"] == 2
        assert sent["estimacion_heuristica"]["total_estimado"] == 5_000_000.0
