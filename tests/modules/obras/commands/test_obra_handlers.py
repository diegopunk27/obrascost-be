from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.obras.commands.create_obra.create_obra_command import CreateObraCommand
from modules.obras.commands.create_obra.create_obra_handler import handle_create_obra
from modules.obras.commands.delete_obra.delete_obra_command import DeleteObraCommand
from modules.obras.commands.delete_obra.delete_obra_handler import handle_delete_obra
from modules.obras.commands.update_obra.update_obra_command import UpdateObraCommand
from modules.obras.commands.update_obra.update_obra_handler import handle_update_obra
from modules.obras.models.obra import Obra
from modules.obras.queries.get_obra.get_obra_handler import handle_get_obra
from modules.obras.queries.get_obra.get_obra_query import GetObraQuery
from modules.obras.queries.list_obras.list_obras_handler import handle_list_obras
from modules.obras.queries.list_obras.list_obras_query import ListObrasQuery


def _make_obra(**kwargs) -> Obra:
    defaults = dict(
        id=1,
        usuario_id=1,
        nombre="Casa Test",
        direccion="",
        provincia_id=1,
        superficie_m2=100.0,
        fecha_inicio=date(2025, 1, 1),
        fecha_fin_estimada=None,
        estado="borrador",
        presupuesto_inicial=None,
    )
    defaults.update(kwargs)
    return Obra(**defaults)


class TestCreateObraHandler:
    @pytest.mark.asyncio
    async def test_crea_obra_correctamente(self):
        session = AsyncMock()
        session.add = MagicMock()
        cmd = CreateObraCommand(
            usuario_id=1,
            nombre="Casa Nueva",
            superficie_m2=120.0,
            fecha_inicio=date(2025, 6, 1),
        )

        async def _refresh(obra):
            obra.id = 99

        session.refresh.side_effect = _refresh

        result = await handle_create_obra(cmd, session)

        assert result.id == 99
        assert result.nombre == "Casa Nueva"
        session.add.assert_called_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_estado_invalido_lanza_unprocessable(self):
        session = AsyncMock()
        cmd = CreateObraCommand(
            usuario_id=1,
            nombre="Casa Test",
            superficie_m2=100.0,
            fecha_inicio=date(2025, 1, 1),
            estado="estado_inexistente",
        )
        with pytest.raises(UnprocessableDomainError):
            await handle_create_obra(cmd, session)


class TestGetObraHandler:
    @pytest.mark.asyncio
    async def test_retorna_obra_propia(self):
        obra = _make_obra(id=10, usuario_id=5)
        session = AsyncMock()
        session.get.return_value = obra

        result = await handle_get_obra(GetObraQuery(id=10, usuario_id=5), session)

        assert result.id == 10

    @pytest.mark.asyncio
    async def test_obra_inexistente_lanza_not_found(self):
        session = AsyncMock()
        session.get.return_value = None

        with pytest.raises(NotFoundError):
            await handle_get_obra(GetObraQuery(id=999, usuario_id=1), session)

    @pytest.mark.asyncio
    async def test_obra_de_otro_usuario_lanza_not_found(self):
        obra = _make_obra(id=10, usuario_id=5)
        session = AsyncMock()
        session.get.return_value = obra

        with pytest.raises(NotFoundError):
            await handle_get_obra(GetObraQuery(id=10, usuario_id=99), session)


class TestListObrasHandler:
    @pytest.mark.asyncio
    async def test_retorna_obras_del_usuario(self):
        obras = [_make_obra(id=1, usuario_id=7), _make_obra(id=2, usuario_id=7)]
        result_mock = MagicMock()
        result_mock.all.return_value = obras
        session = AsyncMock()
        session.exec.return_value = result_mock

        result = await handle_list_obras(ListObrasQuery(usuario_id=7), session)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_lista_vacia_si_no_tiene_obras(self):
        result_mock = MagicMock()
        result_mock.all.return_value = []
        session = AsyncMock()
        session.exec.return_value = result_mock

        result = await handle_list_obras(ListObrasQuery(usuario_id=99), session)

        assert result == []


class TestDeleteObraHandler:
    @pytest.mark.asyncio
    async def test_borra_obra_propia(self):
        obra = _make_obra(id=5, usuario_id=3)
        session = AsyncMock()
        session.get.return_value = obra
        session.delete = AsyncMock()

        await handle_delete_obra(DeleteObraCommand(id=5, usuario_id=3), session)

        session.delete.assert_awaited_once_with(obra)
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_borrar_obra_inexistente_lanza_not_found(self):
        session = AsyncMock()
        session.get.return_value = None

        with pytest.raises(NotFoundError):
            await handle_delete_obra(DeleteObraCommand(id=999, usuario_id=1), session)

    @pytest.mark.asyncio
    async def test_borrar_obra_en_cualquier_estado_funciona(self):
        # La protección contra borrado accidental ocurre en el FE (input de
        # confirmación tipo AWS). El handler permite borrar en cualquier estado
        # siempre que el usuario sea dueño.
        obra = _make_obra(id=7, usuario_id=3, estado="en_progreso")
        session = AsyncMock()
        session.get.return_value = obra
        session.delete = AsyncMock()

        await handle_delete_obra(DeleteObraCommand(id=7, usuario_id=3), session)

        session.delete.assert_awaited_once_with(obra)
        session.commit.assert_awaited_once()


class TestUpdateObraHandler:
    @pytest.mark.asyncio
    async def test_actualiza_campos(self):
        obra = _make_obra(id=8, usuario_id=2, nombre="Antiguo")
        session = AsyncMock()
        session.get.return_value = obra
        session.add = MagicMock()

        cmd = UpdateObraCommand(id=8, nombre="Nuevo Nombre")
        result = await handle_update_obra(cmd, session)

        assert result.nombre == "Nuevo Nombre"
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_actualizar_inexistente_lanza_not_found(self):
        session = AsyncMock()
        session.get.return_value = None

        with pytest.raises(NotFoundError):
            await handle_update_obra(UpdateObraCommand(id=999, nombre="Nuevo"), session)

    @pytest.mark.asyncio
    async def test_estado_invalido_en_update_lanza_unprocessable(self):
        obra = _make_obra(id=10, usuario_id=2)
        session = AsyncMock()
        session.get.return_value = obra
        session.add = MagicMock()

        cmd = UpdateObraCommand(id=10, estado="estado_raro")
        with pytest.raises(UnprocessableDomainError):
            await handle_update_obra(cmd, session)

    @pytest.mark.asyncio
    async def test_transicion_estado_invalida_lanza_unprocessable(self):
        # borrador → finalizada NO es una transición permitida
        obra = _make_obra(id=11, usuario_id=2, estado="borrador")
        session = AsyncMock()
        session.get.return_value = obra
        session.add = MagicMock()

        cmd = UpdateObraCommand(id=11, estado="finalizada")
        with pytest.raises(UnprocessableDomainError):
            await handle_update_obra(cmd, session)

    @pytest.mark.asyncio
    async def test_transicion_estado_valida_actualiza(self):
        # borrador → en_progreso es válida
        obra = _make_obra(id=12, usuario_id=2, estado="borrador")
        session = AsyncMock()
        session.get.return_value = obra
        session.add = MagicMock()

        cmd = UpdateObraCommand(id=12, estado="en_progreso")
        result = await handle_update_obra(cmd, session)

        assert result.estado == "en_progreso"
        session.commit.assert_awaited_once()
