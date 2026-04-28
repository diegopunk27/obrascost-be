from dataclasses import dataclass

# Factor regional multiplicador sobre el costo base de cada rubro.
# Buenos Aires (prov. 1) es la referencia (1.0); norte/NEA más bajo; Patagonia más alto.
_FACTOR_REGIONAL: dict[int, float] = {
    1: 1.0,   # Buenos Aires
    2: 1.05,  # CABA
    3: 0.90,  # Catamarca
    4: 0.88,  # Chaco
    5: 1.12,  # Chubut
    6: 0.95,  # Córdoba
    7: 0.87,  # Corrientes
    8: 1.15,  # Entre Ríos
    9: 0.85,  # Formosa
    10: 0.92, # Jujuy
    11: 0.93, # La Pampa
    12: 0.91, # La Rioja
    13: 0.96, # Mendoza
    14: 0.86, # Misiones
    15: 1.10, # Neuquén
    16: 1.18, # Río Negro
    17: 0.89, # Salta
    18: 0.94, # San Juan
    19: 0.93, # San Luis
    20: 1.20, # Santa Cruz
    21: 0.98, # Santa Fe
    22: 0.90, # Santiago del Estero
    23: 1.25, # Tierra del Fuego
    24: 0.91, # Tucumán
}

DEFAULT_FACTOR = 1.0
MARGEN_ERROR_PCT = 15.0


@dataclass(frozen=True)
class RubroInput:
    nombre: str
    costo_referencia_m2: float


@dataclass(frozen=True)
class EstimacionHeuristica:
    total_estimado: float
    desglose_por_rubro: dict[str, float]
    margen_error_pct: float


def calcular_estimacion(
    superficie_m2: float,
    provincia_id: int | None,
    rubros: list[RubroInput],
) -> EstimacionHeuristica:
    factor = _FACTOR_REGIONAL.get(provincia_id or 0, DEFAULT_FACTOR)
    desglose: dict[str, float] = {}
    for r in rubros:
        desglose[r.nombre] = round(superficie_m2 * r.costo_referencia_m2 * factor, 2)
    total = round(sum(desglose.values()), 2)
    return EstimacionHeuristica(
        total_estimado=total,
        desglose_por_rubro=desglose,
        margen_error_pct=MARGEN_ERROR_PCT,
    )
