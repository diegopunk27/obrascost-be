from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import UnprocessableDomainError
from modules.obras.commands.create_obra.create_obra_command import CreateObraCommand
from modules.obras.models.obra import Obra
from modules.obras.schemas import ESTADOS_VALIDOS, ObraRead


@CommandBus.register(CreateObraCommand)
async def handle_create_obra(command: CreateObraCommand, session: AsyncSession) -> ObraRead:
    if command.estado not in ESTADOS_VALIDOS:
        raise UnprocessableDomainError(f"Estado inválido: {command.estado}")
    obra = Obra(**command.model_dump())
    session.add(obra)
    await session.commit()
    await session.refresh(obra)
    return ObraRead.model_validate(obra, from_attributes=True)
