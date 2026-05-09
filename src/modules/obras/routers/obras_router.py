from fastapi import APIRouter, Depends, status
from sqlmodel import select

from common.auth.dependencies import get_current_user
from common.auth.schemas import UserSchema
from common.cqrs.command_bus import CommandBus
from common.cqrs.deps import get_command_bus, get_query_bus
from common.cqrs.query_bus import QueryBus
from common.database.session import get_session
from modules.obras.commands.create_obra.create_obra_command import CreateObraCommand
from modules.obras.commands.delete_obra.delete_obra_command import DeleteObraCommand
from modules.obras.commands.update_obra.update_obra_command import UpdateObraCommand
from modules.obras.estimacion.ai_estimator_client import enriquecer_con_ia
from modules.obras.estimacion.heuristic_estimator import RubroInput, calcular_estimacion
from modules.obras.queries.get_obra.get_obra_query import GetObraQuery
from modules.obras.queries.list_obras.list_obras_query import ListObrasQuery
from modules.obras.schemas import EstimacionResult, ObraCreate, ObraRead, ObraUpdate
from modules.rubros.models.rubro import Rubro

router = APIRouter(prefix="/obras", tags=["Obras"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[ObraRead])
async def list_obras(
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
    current_user: UserSchema = Depends(get_current_user),
) -> list[ObraRead]:
    return await bus.execute(ListObrasQuery(usuario_id=current_user.id), session=session)


@router.get("/{obra_id}", response_model=ObraRead)
async def get_obra(
    obra_id: int,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
    current_user: UserSchema = Depends(get_current_user),
) -> ObraRead:
    return await bus.execute(GetObraQuery(id=obra_id, usuario_id=current_user.id), session=session)


@router.post("", response_model=ObraRead, status_code=status.HTTP_201_CREATED)
async def create_obra(
    body: ObraCreate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
    current_user: UserSchema = Depends(get_current_user),
) -> ObraRead:
    cmd = CreateObraCommand(usuario_id=current_user.id, **body.model_dump())
    return await bus.execute(cmd, session=session)


@router.patch("/{obra_id}", response_model=ObraRead)
async def update_obra(
    obra_id: int,
    body: ObraUpdate,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> ObraRead:
    return await bus.execute(
        UpdateObraCommand(id=obra_id, **body.model_dump(exclude_none=True)), session=session
    )


@router.delete("/{obra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_obra(
    obra_id: int,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
    current_user: UserSchema = Depends(get_current_user),
) -> None:
    await bus.execute(DeleteObraCommand(id=obra_id, usuario_id=current_user.id), session=session)


@router.post("/{obra_id}/estimacion", response_model=EstimacionResult)
async def estimar_obra(
    obra_id: int,
    con_ia: bool = False,
    bus: QueryBus = Depends(get_query_bus),
    session=Depends(get_session),
    current_user: UserSchema = Depends(get_current_user),
) -> EstimacionResult:
    obra_read = await bus.execute(
        GetObraQuery(id=obra_id, usuario_id=current_user.id), session=session
    )
    rubros_result = await session.exec(select(Rubro).where(Rubro.activo == True))  # noqa: E712
    rubros = [
        RubroInput(nombre=r.nombre, costo_referencia_m2=r.costo_referencia_m2)
        for r in rubros_result.all()
    ]
    estimacion = calcular_estimacion(
        superficie_m2=obra_read.superficie_m2,
        provincia_id=obra_read.provincia_id,
        rubros=rubros,
    )
    if con_ia:
        sugerencia, ajuste, alertas = await enriquecer_con_ia(
            nombre_obra=obra_read.nombre,
            superficie_m2=obra_read.superficie_m2,
            provincia_id=obra_read.provincia_id,
            estimacion_base=estimacion,
        )
        return EstimacionResult(
            total_estimado=estimacion.total_estimado,
            desglose_por_rubro=estimacion.desglose_por_rubro,
            margen_error_pct=estimacion.margen_error_pct,
            fuente="heuristica+ia" if sugerencia else "heuristica",
            sugerencia_ia=sugerencia,
            ajuste_recomendado_pct=ajuste,
            alertas=alertas,
        )
    return EstimacionResult(
        total_estimado=estimacion.total_estimado,
        desglose_por_rubro=estimacion.desglose_por_rubro,
        margen_error_pct=estimacion.margen_error_pct,
    )
