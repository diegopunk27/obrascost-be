from datetime import date

import pytest
from pydantic import ValidationError

from modules.obras.schemas import ObraCreate


class TestObraCreateValidation:
    def test_valido_minimo(self):
        obra = ObraCreate(
            nombre="Casa Mínima",
            superficie_m2=50.0,
            fecha_inicio=date(2025, 1, 1),
        )
        assert obra.nombre == "Casa Mínima"
        assert obra.estado == "borrador"

    def test_nombre_muy_corto_falla(self):
        with pytest.raises(ValidationError) as exc:
            ObraCreate(nombre="AB", superficie_m2=50, fecha_inicio=date(2025, 1, 1))
        assert "nombre" in str(exc.value)

    def test_nombre_muy_largo_falla(self):
        with pytest.raises(ValidationError):
            ObraCreate(nombre="X" * 201, superficie_m2=50, fecha_inicio=date(2025, 1, 1))

    def test_superficie_cero_falla(self):
        with pytest.raises(ValidationError) as exc:
            ObraCreate(nombre="Casa Test", superficie_m2=0, fecha_inicio=date(2025, 1, 1))
        assert "superficie_m2" in str(exc.value)

    def test_superficie_negativa_falla(self):
        with pytest.raises(ValidationError):
            ObraCreate(nombre="Casa Test", superficie_m2=-10, fecha_inicio=date(2025, 1, 1))

    def test_presupuesto_negativo_falla(self):
        with pytest.raises(ValidationError):
            ObraCreate(
                nombre="Casa Test",
                superficie_m2=100,
                fecha_inicio=date(2025, 1, 1),
                presupuesto_inicial=-1.0,
            )

    def test_presupuesto_cero_es_valido(self):
        obra = ObraCreate(
            nombre="Casa Test",
            superficie_m2=100,
            fecha_inicio=date(2025, 1, 1),
            presupuesto_inicial=0.0,
        )
        assert obra.presupuesto_inicial == 0.0

    def test_provincia_id_none_es_valido(self):
        obra = ObraCreate(nombre="Casa Test", superficie_m2=100, fecha_inicio=date(2025, 1, 1))
        assert obra.provincia_id is None

    def test_estado_default_es_borrador(self):
        obra = ObraCreate(nombre="Casa Test", superficie_m2=100, fecha_inicio=date(2025, 1, 1))
        assert obra.estado == "borrador"

    def test_fecha_fin_estimada_none_es_valido(self):
        obra = ObraCreate(nombre="Casa Test", superficie_m2=100, fecha_inicio=date(2025, 1, 1))
        assert obra.fecha_fin_estimada is None

    def test_todos_los_campos_opcionales(self):
        obra = ObraCreate(
            nombre="Casa Completa",
            superficie_m2=200,
            fecha_inicio=date(2025, 3, 1),
            fecha_fin_estimada=date(2026, 3, 1),
            direccion="Av. Siempre Viva 123",
            provincia_id=2,
            estado="en_progreso",
            presupuesto_inicial=15_000_000.0,
        )
        assert obra.provincia_id == 2
        assert obra.estado == "en_progreso"
