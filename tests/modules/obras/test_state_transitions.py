"""Unit tests para la máquina de estados de obras."""

import pytest

from modules.obras.schemas import TRANSICIONES_VALIDAS, es_transicion_valida


class TestTransicionesValidas:
    @pytest.mark.parametrize(
        "actual,nuevo",
        [
            ("borrador", "en_progreso"),
            ("borrador", "cancelada"),
            ("en_progreso", "pausada"),
            ("en_progreso", "finalizada"),
            ("en_progreso", "cancelada"),
            ("pausada", "en_progreso"),
            ("pausada", "cancelada"),
        ],
    )
    def test_transiciones_permitidas(self, actual, nuevo):
        assert es_transicion_valida(actual, nuevo)

    @pytest.mark.parametrize(
        "actual,nuevo",
        [
            ("borrador", "pausada"),
            ("borrador", "finalizada"),
            ("en_progreso", "borrador"),
            ("pausada", "finalizada"),
            ("pausada", "borrador"),
            # estados terminales no permiten transiciones
            ("finalizada", "borrador"),
            ("finalizada", "en_progreso"),
            ("finalizada", "cancelada"),
            ("cancelada", "borrador"),
            ("cancelada", "en_progreso"),
        ],
    )
    def test_transiciones_prohibidas(self, actual, nuevo):
        assert not es_transicion_valida(actual, nuevo)

    @pytest.mark.parametrize(
        "estado",
        ["borrador", "en_progreso", "pausada", "finalizada", "cancelada"],
    )
    def test_misma_transicion_es_idempotente(self, estado):
        assert es_transicion_valida(estado, estado)

    def test_estado_inexistente_no_permite_transicion(self):
        assert not es_transicion_valida("estado_raro", "borrador")

    def test_estados_terminales_no_tienen_transiciones(self):
        assert TRANSICIONES_VALIDAS["finalizada"] == set()
        assert TRANSICIONES_VALIDAS["cancelada"] == set()
