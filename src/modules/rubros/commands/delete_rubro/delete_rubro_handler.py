from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError
from modules.rubros.commands.delete_rubro.delete_rubro_command import DeleteRubroCommand
from modules.rubros.models.rubro import Rubro


@CommandBus.register(DeleteRubroCommand)
async def handle_delete_rubro(command: DeleteRubroCommand, session: AsyncSession) -> None:
    rubro = await session.get(Rubro, command.id)
    if rubro is None:
        raise NotFoundError(f"Rubro {command.id} no encontrado")
    await session.delete(rubro)
    await session.commit()
