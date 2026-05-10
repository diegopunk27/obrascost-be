import asyncio
import json
import logging

import httpx

from common.config.settings import get_settings
from modules.obras.estimacion.heuristic_estimator import EstimacionHeuristica

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(65.0, connect=10.0)
_RETRY_STATUS = {502, 503, 504}
_MAX_ATTEMPTS = 3
_RETRY_DELAYS_SECONDS = (5, 15)

_ALERTA_TIMEOUT = (
    "El análisis con IA tardó demasiado (posible arranque en frío del servidor). "
    "Mostramos la estimación heurística."
)
_ALERTA_FALLBACK = (
    "El análisis con IA no está disponible en este momento. Mostramos la estimación heurística."
)


async def _post_con_retry(client: httpx.AsyncClient, url: str, payload: dict) -> httpx.Response:
    """POST con reintentos para 502/503/504 (típicos del cold start de Render free tier)."""
    last_response: httpx.Response | None = None
    for attempt in range(_MAX_ATTEMPTS):
        response = await client.post(url, json=payload)
        if response.status_code not in _RETRY_STATUS:
            return response
        last_response = response
        if attempt < _MAX_ATTEMPTS - 1:
            delay = _RETRY_DELAYS_SECONDS[attempt]
            logger.info(
                "ai_estimator_client recibió %s, reintentando en %ss (intento %s/%s)",
                response.status_code,
                delay,
                attempt + 2,
                _MAX_ATTEMPTS,
            )
            await asyncio.sleep(delay)
    assert last_response is not None
    return last_response


async def enriquecer_con_ia(
    nombre_obra: str,
    superficie_m2: float,
    provincia_id: int | None,
    estimacion_base: EstimacionHeuristica,
) -> tuple[str | None, float | None, list[str]]:
    """Llama a api-multiagente y retorna (sugerencia, ajuste_pct, alertas).

    Siempre retorna sin lanzar excepción — degrada gracefully con una alerta visible.
    """
    settings = get_settings()
    payload = {
        "nombre_obra": nombre_obra,
        "superficie_m2": superficie_m2,
        "provincia_id": provincia_id,
        "estimacion_heuristica": {
            "total_estimado": estimacion_base.total_estimado,
            "desglose_por_rubro": estimacion_base.desglose_por_rubro,
            "margen_error_pct": estimacion_base.margen_error_pct,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await _post_con_retry(
                client, f"{settings.ai_api_base_url}/estimacion-obra", payload
            )
            response.raise_for_status()
            data = response.json()
            sugerencia = data.get("sugerencia_narrativa") or data.get("sugerencia")
            ajuste = data.get("ajuste_recomendado_pct")
            alertas = data.get("alertas", [])
            return str(sugerencia) if sugerencia else None, ajuste, alertas
    except httpx.TimeoutException as exc:
        logger.warning("ai_estimator_client timeout (%ss): %s", _TIMEOUT.read, exc)
        return None, None, [_ALERTA_TIMEOUT]
    except Exception as exc:
        logger.warning(
            "ai_estimator_client falló contra %s — %s: %s",
            settings.ai_api_base_url,
            type(exc).__name__,
            exc,
        )
        return None, None, [_ALERTA_FALLBACK]


def _parse_json_block(text: str) -> dict:
    """Extrae el primer bloque JSON de un texto de respuesta LLM."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {}
