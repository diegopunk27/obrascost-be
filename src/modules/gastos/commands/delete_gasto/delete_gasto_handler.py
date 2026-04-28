from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.gastos.commands.delete_gasto.delete_gasto_command import DeleteGastoCommand
from modules.gastos.models.gasto import Gasto


@CommandBus.register(DeleteGastoCommand)
async def handle_delete_gasto(command: DeleteGastoCommand, session: AsyncSession) -> None:
    gasto = await session.get(Gasto, command.id)
    if gasto is None:
        raise NotFoundError(f"Gasto {command.id} no encontrado")
    if gasto.obra_id != command.obra_id:
        raise UnprocessableDomainError("El gasto no pertenece a esta obra")
    await session.delete(gasto)
    await session.commit()
