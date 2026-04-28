from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.query_bus import QueryBus
from common.exceptions.domain import NotFoundError
from modules.gastos.models.gasto import Gasto
from modules.gastos.queries.get_gasto.get_gasto_query import GetGastoQuery
from modules.gastos.schemas import GastoRead


@QueryBus.register(GetGastoQuery)
async def handle_get_gasto(query: GetGastoQuery, session: AsyncSession) -> GastoRead:
    gasto = await session.get(Gasto, query.id)
    if gasto is None or gasto.obra_id != query.obra_id:
        raise NotFoundError(f"Gasto {query.id} no encontrado")
    return GastoRead.model_validate(gasto, from_attributes=True)
