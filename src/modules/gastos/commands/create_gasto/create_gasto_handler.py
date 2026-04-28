from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.command_bus import CommandBus
from modules.gastos.commands.create_gasto.create_gasto_command import CreateGastoCommand
from modules.gastos.models.gasto import Gasto
from modules.gastos.schemas import GastoRead


@CommandBus.register(CreateGastoCommand)
async def handle_create_gasto(command: CreateGastoCommand, session: AsyncSession) -> GastoRead:
    gasto = Gasto(**command.model_dump())
    session.add(gasto)
    await session.commit()
    await session.refresh(gasto)
    return GastoRead.model_validate(gasto, from_attributes=True)
