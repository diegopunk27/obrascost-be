from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.query_bus import QueryBus
from modules.rubros.models.rubro import Rubro
from modules.rubros.queries.list_rubros.list_rubros_query import ListRubrosQuery
from modules.rubros.schemas import RubroRead


@QueryBus.register(ListRubrosQuery)
async def handle_list_rubros(query: ListRubrosQuery, session: AsyncSession) -> list[RubroRead]:
    stmt = select(Rubro)
    if query.solo_activos:
        stmt = stmt.where(Rubro.activo == True)  # noqa: E712
    result = await session.exec(stmt)
    return [RubroRead.model_validate(r, from_attributes=True) for r in result.all()]
