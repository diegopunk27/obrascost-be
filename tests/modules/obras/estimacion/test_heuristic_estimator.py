import pytest

from modules.obras.estimacion.heuristic_estimator import (
    DEFAULT_FACTOR,
    MARGEN_ERROR_PCT,
    RubroInput,
    calcular_estimacion,
)

RUBROS_BASE = [
    RubroInput(nombre="Estructura", costo_referencia_m2=35_000.0),
    RubroInput(nombre="Mampostería", costo_referencia_m2=25_000.0),
]


class TestCalcularEstimacion:
    def test_sin_rubros_retorna_total_cero(self):
        result = calcular_estimacion(superficie_m2=100, provincia_id=1, rubros=[])
        assert result.total_estimado == 0.0
        assert result.desglose_por_rubro == {}
        assert result.margen_error_pct == MARGEN_ERROR_PCT

    def test_un_rubro_calculo_basico(self):
        rubros = [RubroInput(nombre="Estructura", costo_referencia_m2=10_000.0)]
        result = calcular_estimacion(superficie_m2=100, provincia_id=1, rubros=rubros)
        # BA factor = 1.0 → 100 * 10_000 * 1.0 = 1_000_000
        assert result.total_estimado == 1_000_000.0
        assert result.desglose_por_rubro["Estructura"] == 1_000_000.0

    def test_factor_regional_caba(self):
        rubros = [RubroInput(nombre="Estructura", costo_referencia_m2=10_000.0)]
        result = calcular_estimacion(superficie_m2=100, provincia_id=2, rubros=rubros)
        # CABA factor = 1.05
        assert result.total_estimado == pytest.approx(1_050_000.0)

    def test_factor_regional_patagonia(self):
        rubros = [RubroInput(nombre="Estructura", costo_referencia_m2=10_000.0)]
        result = calcular_estimacion(superficie_m2=100, provincia_id=23, rubros=rubros)
        # Tierra del Fuego factor = 1.25
        assert result.total_estimado == pytest.approx(1_250_000.0)

    def test_provincia_desconocida_usa_factor_default(self):
        rubros = [RubroInput(nombre="Estructura", costo_referencia_m2=10_000.0)]
        result_desconocida = calcular_estimacion(superficie_m2=100, provincia_id=999, rubros=rubros)
        result_default = calcular_estimacion(superficie_m2=100, provincia_id=1, rubros=rubros)
        # Factor desconocido == DEFAULT_FACTOR == 1.0 == factor BA
        assert result_desconocida.total_estimado == result_default.total_estimado
        assert DEFAULT_FACTOR == 1.0

    def test_provincia_none_usa_factor_default(self):
        rubros = [RubroInput(nombre="Estructura", costo_referencia_m2=10_000.0)]
        result = calcular_estimacion(superficie_m2=100, provincia_id=None, rubros=rubros)
        assert result.total_estimado == pytest.approx(100 * 10_000.0 * DEFAULT_FACTOR)

    def test_multiples_rubros_desglose_correcto(self):
        result = calcular_estimacion(superficie_m2=100, provincia_id=1, rubros=RUBROS_BASE)
        assert result.desglose_por_rubro["Estructura"] == 3_500_000.0
        assert result.desglose_por_rubro["Mampostería"] == 2_500_000.0
        assert result.total_estimado == 6_000_000.0

    @pytest.mark.parametrize(
        "superficie, provincia_id, costo_m2, expected_total",
        [
            (50, 1, 30_000.0, 1_500_000.0),  # pequeño, BA
            (200, 1, 30_000.0, 6_000_000.0),  # grande, BA
            (100, 2, 30_000.0, 3_150_000.0),  # CABA 1.05
            (100, 5, 30_000.0, 3_360_000.0),  # Chubut 1.12
            (100, 9, 30_000.0, 2_550_000.0),  # Formosa 0.85
            (0.1, 1, 100_000.0, 10_000.0),  # superficie mínima
        ],
    )
    def test_parametrizado_superficie_y_provincia(
        self, superficie, provincia_id, costo_m2, expected_total
    ):
        rubros = [RubroInput(nombre="Test", costo_referencia_m2=costo_m2)]
        result = calcular_estimacion(
            superficie_m2=superficie, provincia_id=provincia_id, rubros=rubros
        )
        assert result.total_estimado == pytest.approx(expected_total, rel=1e-3)

    def test_margen_error_siempre_constante(self):
        result = calcular_estimacion(superficie_m2=500, provincia_id=1, rubros=RUBROS_BASE)
        assert result.margen_error_pct == MARGEN_ERROR_PCT

    def test_resultado_es_inmutable(self):
        result = calcular_estimacion(superficie_m2=100, provincia_id=1, rubros=RUBROS_BASE)
        with pytest.raises((AttributeError, TypeError)):
            result.total_estimado = 0  # type: ignore[misc]

    def test_nombres_rubros_preservados_en_desglose(self):
        rubros = [RubroInput(nombre="Inst. eléctrica", costo_referencia_m2=15_000.0)]
        result = calcular_estimacion(superficie_m2=50, provincia_id=1, rubros=rubros)
        assert "Inst. eléctrica" in result.desglose_por_rubro
