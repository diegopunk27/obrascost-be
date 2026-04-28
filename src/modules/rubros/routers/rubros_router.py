from fastapi import APIRouter, Depends, status

from common.auth.dependencies import get_current_user
from common.cqrs.command_bus import CommandBus
from common.cqrs.deps import get_command_bus, get_query_bus
from common.cqrs.query_bus import QueryBus
from common.database.session import get_session
from modules.rubros.commands.create_rubro.create_rubro_command import CreateRubroCommand
from modules.rubros.commands.delete_rubro.delete_rubro_command import DeleteRubroCommand
from modules.rubros.commands.update_rubro.update_rubro_command import UpdateRubroCommand
from modules.rubros.queries.get_rubro.get_rubro_query import GetRubroQuery
from modules.rubros.queries.list_rubros.list_rubros_query import ListRubrosQuery
from modules.rubros.schemas import RubroCreate, RubroRead, RubroUpdate

router = APIRouter(prefix="/rubros", tags=["Rubros"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[RubroRead])
async def list_rubros(
    solo_activos: bool = True,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
) -> list[RubroRead]:
    return await bus.execute(ListRubrosQuery(solo_activos=solo_activos), session=session)


@router.get("/{rubro_id}", response_model=RubroRead)
async def get_rubro(
    rubro_id: int,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
) -> RubroRead:
    return await bus.execute(GetRubroQuery(id=rubro_id), session=session)


@router.post("", response_model=RubroRead, status_code=status.HTTP_201_CREATED)
async def create_rubro(
    body: RubroCreate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> RubroRead:
    return await bus.execute(CreateRubroCommand(**body.model_dump()), session=session)


@router.patch("/{rubro_id}", response_model=RubroRead)
async def update_rubro(
    rubro_id: int,
    body: RubroUpdate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> RubroRead:
    return await bus.execute(
        UpdateRubroCommand(id=rubro_id, **body.model_dump(exclude_none=True)), session=session
    )


@router.delete("/{rubro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rubro(
    rubro_id: int,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> None:
    await bus.execute(DeleteRubroCommand(id=rubro_id), session=session)
