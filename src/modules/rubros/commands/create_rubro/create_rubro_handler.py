from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import ConflictError
from modules.rubros.commands.create_rubro.create_rubro_command import CreateRubroCommand
from modules.rubros.models.rubro import Rubro
from modules.rubros.schemas import RubroRead


@CommandBus.register(CreateRubroCommand)
async def handle_create_rubro(command: CreateRubroCommand, session: AsyncSession) -> RubroRead:
    existing = await session.exec(select(Rubro).where(Rubro.nombre == command.nombre))
    if existing.first():
        raise ConflictError(f"Ya existe un rubro con nombre '{command.nombre}'")
    rubro = Rubro(
        nombre=command.nombre,
        descripcion=command.descripcion,
        costo_referencia_m2=command.costo_referencia_m2,
    )
    session.add(rubro)
    await session.commit()
    await session.refresh(rubro)
    return RubroRead.model_validate(rubro, from_attributes=True)
