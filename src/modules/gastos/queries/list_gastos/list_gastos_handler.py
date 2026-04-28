from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from common.cqrs.query_bus import QueryBus
from modules.gastos.models.gasto import Gasto
from modules.gastos.queries.list_gastos.list_gastos_query import ListGastosQuery
from modules.gastos.schemas import GastoRead


@QueryBus.register(ListGastosQuery)
async def handle_list_gastos(query: ListGastosQuery, session: AsyncSession) -> list[GastoRead]:
    result = await session.exec(select(Gasto).where(Gasto.obra_id == query.obra_id))
    return [GastoRead.model_validate(g, from_attributes=True) for g in result.all()]
