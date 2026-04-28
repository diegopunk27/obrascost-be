from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError
from modules.rubros.commands.update_rubro.update_rubro_command import UpdateRubroCommand
from modules.rubros.models.rubro import Rubro
from modules.rubros.schemas import RubroRead


@CommandBus.register(UpdateRubroCommand)
async def handle_update_rubro(command: UpdateRubroCommand, session: AsyncSession) -> RubroRead:
    rubro = await session.get(Rubro, command.id)
    if rubro is None:
        raise NotFoundError(f"Rubro {command.id} no encontrado")
    updates = command.model_dump(exclude={"id"}, exclude_none=True)
    for field, value in updates.items():
        setattr(rubro, field, value)
    session.add(rubro)
    await session.commit()
    await session.refresh(rubro)
    return RubroRead.model_validate(rubro, from_attributes=True)
