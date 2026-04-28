from fastapi import APIRouter, Depends, status

from common.auth.dependencies import get_current_user
from common.cqrs.command_bus import CommandBus
from common.cqrs.deps import get_command_bus, get_query_bus
from common.cqrs.query_bus import QueryBus
from common.database.session import get_session
from modules.gastos.commands.create_gasto.create_gasto_command import CreateGastoCommand
from modules.gastos.commands.delete_gasto.delete_gasto_command import DeleteGastoCommand
from modules.gastos.commands.update_gasto.update_gasto_command import UpdateGastoCommand
from modules.gastos.queries.get_gasto.get_gasto_query import GetGastoQuery
from modules.gastos.queries.list_gastos.list_gastos_query import ListGastosQuery
from modules.gastos.schemas import GastoCreate, GastoRead, GastoUpdate

router = APIRouter(
    prefix="/obras/{obra_id}/gastos",
    tags=["Gastos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[GastoRead])
async def list_gastos(
    obra_id: int,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
) -> list[GastoRead]:
    return await bus.execute(ListGastosQuery(obra_id=obra_id), session=session)


@router.get("/{gasto_id}", response_model=GastoRead)
async def get_gasto(
    obra_id: int,
    gasto_id: int,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
) -> GastoRead:
    return await bus.execute(GetGastoQuery(id=gasto_id, obra_id=obra_id), session=session)


@router.post("", response_model=GastoRead, status_code=status.HTTP_201_CREATED)
async def create_gasto(
    obra_id: int,
    body: GastoCreate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> GastoRead:
    return await bus.execute(
        CreateGastoCommand(obra_id=obra_id, **body.model_dump()), session=session
    )


@router.patch("/{gasto_id}", response_model=GastoRead)
async def update_gasto(
    obra_id: int,
    gasto_id: int,
    body: GastoUpdate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> GastoRead:
    return await bus.execute(
        UpdateGastoCommand(id=gasto_id, obra_id=obra_id, **body.model_dump(exclude_none=True)),
        session=session,
    )


@router.delete("/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gasto(
    obra_id: int,
    gasto_id: int,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> None:
    await bus.execute(DeleteGastoCommand(id=gasto_id, obra_id=obra_id), session=session)
