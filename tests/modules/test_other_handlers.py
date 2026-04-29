from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.exceptions.domain import ConflictError, NotFoundError, UnprocessableDomainError
from modules.gastos.commands.create_gasto.create_gasto_command import CreateGastoCommand
from modules.gastos.commands.create_gasto.create_gasto_handler import handle_create_gasto
from modules.gastos.commands.delete_gasto.delete_gasto_command import DeleteGastoCommand
from modules.gastos.commands.delete_gasto.delete_gasto_handler import handle_delete_gasto
from modules.gastos.models.gasto import Gasto
from modules.gastos.queries.list_gastos.list_gastos_handler import handle_list_gastos
from modules.gastos.queries.list_gastos.list_gastos_query import ListGastosQuery
from modules.rubros.commands.create_rubro.create_rubro_command import CreateRubroCommand
from modules.rubros.commands.create_rubro.create_rubro_handler import handle_create_rubro
from modules.rubros.commands.delete_rubro.delete_rubro_command import DeleteRubroCommand
from modules.rubros.commands.delete_rubro.delete_rubro_handler import handle_delete_rubro
from modules.rubros.models.rubro import Rubro
from modules.rubros.queries.list_rubros.list_rubros_handler import handle_list_rubros
from modules.rubros.queries.list_rubros.list_rubros_query import ListRubrosQuery


def _scalars_first(value):
    s = MagicMock()
    s.first.return_value = value
    return s


def _exec_result(items):
    r = MagicMock()
    r.first.return_value = items[0] if items else None
    r.all.return_value = items
    return r


class TestCreateGastoHandler:
    @pytest.mark.asyncio
    async def test_crea_gasto(self):
        session = AsyncMock()
        session.add = MagicMock()

        async def _refresh(g):
            g.id = 11

        session.refresh.side_effect = _refresh
        cmd = CreateGastoCommand(
            obra_id=1,
            descripcion="Bolsas de cemento",
            monto=15000.0,
            fecha=date(2025, 5, 1),
        )
        result = await handle_create_gasto(cmd, session)
        assert result.id == 11
        session.commit.assert_awaited_once()


class TestDeleteGastoHandler:
    @pytest.mark.asyncio
    async def test_borra_gasto_propio(self):
        gasto = Gasto(id=1, obra_id=2, descripcion="Test", monto=100, fecha=date(2025, 1, 1))
        session = AsyncMock()
        session.get.return_value = gasto
        session.delete = AsyncMock()

        await handle_delete_gasto(DeleteGastoCommand(id=1, obra_id=2), session)

        session.delete.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_gasto_inexistente_lanza_not_found(self):
        session = AsyncMock()
        session.get.return_value = None
        with pytest.raises(NotFoundError):
            await handle_delete_gasto(DeleteGastoCommand(id=999, obra_id=1), session)

    @pytest.mark.asyncio
    async def test_gasto_de_otra_obra_lanza_unprocessable(self):
        gasto = Gasto(id=1, obra_id=99, descripcion="Test", monto=100, fecha=date(2025, 1, 1))
        session = AsyncMock()
        session.get.return_value = gasto
        with pytest.raises(UnprocessableDomainError):
            await handle_delete_gasto(DeleteGastoCommand(id=1, obra_id=2), session)


class TestListGastosHandler:
    @pytest.mark.asyncio
    async def test_retorna_gastos_de_obra(self):
        gastos = [
            Gasto(id=1, obra_id=5, descripcion="A", monto=100, fecha=date(2025, 1, 1)),
            Gasto(id=2, obra_id=5, descripcion="B", monto=200, fecha=date(2025, 1, 2)),
        ]
        session = AsyncMock()
        session.exec.return_value = _exec_result(gastos)
        result = await handle_list_gastos(ListGastosQuery(obra_id=5), session)
        assert len(result) == 2


class TestCreateRubroHandler:
    @pytest.mark.asyncio
    async def test_crea_rubro_nuevo(self):
        session = AsyncMock()
        session.exec.return_value = _exec_result([])
        session.add = MagicMock()

        async def _refresh(r):
            r.id = 7

        session.refresh.side_effect = _refresh
        cmd = CreateRubroCommand(nombre="Estructura", descripcion="", costo_referencia_m2=35000.0)
        result = await handle_create_rubro(cmd, session)
        assert result.id == 7

    @pytest.mark.asyncio
    async def test_rubro_duplicado_lanza_conflict(self):
        existing = Rubro(id=1, nombre="Estructura", descripcion="", costo_referencia_m2=30000.0, activo=True)
        session = AsyncMock()
        session.exec.return_value = _exec_result([existing])

        cmd = CreateRubroCommand(nombre="Estructura", descripcion="", costo_referencia_m2=35000.0)
        with pytest.raises(ConflictError):
            await handle_create_rubro(cmd, session)


class TestDeleteRubroHandler:
    @pytest.mark.asyncio
    async def test_borra_rubro_existente(self):
        rubro = Rubro(id=3, nombre="Pintura", descripcion="", costo_referencia_m2=10000.0, activo=True)
        session = AsyncMock()
        session.get.return_value = rubro
        session.delete = AsyncMock()
        await handle_delete_rubro(DeleteRubroCommand(id=3), session)
        session.delete.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rubro_inexistente_lanza_not_found(self):
        session = AsyncMock()
        session.get.return_value = None
        with pytest.raises(NotFoundError):
            await handle_delete_rubro(DeleteRubroCommand(id=999), session)


class TestListRubrosHandler:
    @pytest.mark.asyncio
    async def test_lista_solo_activos(self):
        rubros = [Rubro(id=1, nombre="A", descripcion="", costo_referencia_m2=1000, activo=True)]
        session = AsyncMock()
        session.exec.return_value = _exec_result(rubros)
        result = await handle_list_rubros(ListRubrosQuery(solo_activos=True), session)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_lista_todos_si_solo_activos_false(self):
        rubros = [
            Rubro(id=1, nombre="A", descripcion="", costo_referencia_m2=1000, activo=True),
            Rubro(id=2, nombre="B", descripcion="", costo_referencia_m2=2000, activo=False),
        ]
        session = AsyncMock()
        session.exec.return_value = _exec_result(rubros)
        result = await handle_list_rubros(ListRubrosQuery(solo_activos=False), session)
        assert len(result) == 2
