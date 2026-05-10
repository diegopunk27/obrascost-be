from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.obras.commands.update_obra.update_obra_command import UpdateObraCommand
from modules.obras.models.obra import Obra
from modules.obras.schemas import ESTADOS_VALIDOS, ObraRead, es_transicion_valida


@CommandBus.register(UpdateObraCommand)
async def handle_update_obra(command: UpdateObraCommand, session: AsyncSession) -> ObraRead:
    obra = await session.get(Obra, command.id)
    if obra is None:
        raise NotFoundError(f"Obra {command.id} no encontrada")
    updates = command.model_dump(exclude={"id"}, exclude_none=True)
    if "estado" in updates:
        if updates["estado"] not in ESTADOS_VALIDOS:
            raise UnprocessableDomainError(f"Estado inválido: {updates['estado']}")
        if not es_transicion_valida(obra.estado, updates["estado"]):
            raise UnprocessableDomainError(
                f"Transición de estado inválida: '{obra.estado}' → '{updates['estado']}'."
            )
    for field, value in updates.items():
        setattr(obra, field, value)
    session.add(obra)
    await session.commit()
    await session.refresh(obra)
    return ObraRead.model_validate(obra, from_attributes=True)
