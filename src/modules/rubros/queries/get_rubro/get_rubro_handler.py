from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.query_bus import QueryBus
from common.exceptions.domain import NotFoundError
from modules.rubros.models.rubro import Rubro
from modules.rubros.queries.get_rubro.get_rubro_query import GetRubroQuery
from modules.rubros.schemas import RubroRead


@QueryBus.register(GetRubroQuery)
async def handle_get_rubro(query: GetRubroQuery, session: AsyncSession) -> RubroRead:
    rubro = await session.get(Rubro, query.id)
    if rubro is None:
        raise NotFoundError(f"Rubro {query.id} no encontrado")
    return RubroRead.model_validate(rubro, from_attributes=True)
