from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.gastos.commands.update_gasto.update_gasto_command import UpdateGastoCommand
from modules.gastos.models.gasto import Gasto
from modules.gastos.schemas import GastoRead


@CommandBus.register(UpdateGastoCommand)
async def handle_update_gasto(command: UpdateGastoCommand, session: AsyncSession) -> GastoRead:
    gasto = await session.get(Gasto, command.id)
    if gasto is None:
        raise NotFoundError(f"Gasto {command.id} no encontrado")
    if gasto.obra_id != command.obra_id:
        raise UnprocessableDomainError("El gasto no pertenece a esta obra")
    updates = command.model_dump(exclude={"id", "obra_id"}, exclude_none=True)
    for field, value in updates.items():
        setattr(gasto, field, value)
    session.add(gasto)
    await session.commit()
    await session.refresh(gasto)
    return GastoRead.model_validate(gasto, from_attributes=True)
