from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.obras.commands.delete_obra.delete_obra_command import DeleteObraCommand
from modules.obras.models.obra import Obra


@CommandBus.register(DeleteObraCommand)
async def handle_delete_obra(command: DeleteObraCommand, session: AsyncSession) -> None:
    obra = await session.get(Obra, command.id)
    if obra is None:
        raise NotFoundError(f"Obra {command.id} no encontrada")
    if obra.usuario_id != command.usuario_id:
        raise UnprocessableDomainError("No tenés permiso para eliminar esta obra")
    await session.delete(obra)
    await session.commit()
