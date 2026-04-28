from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.query_bus import QueryBus
from common.exceptions.domain import NotFoundError
from modules.obras.models.obra import Obra
from modules.obras.queries.get_obra.get_obra_query import GetObraQuery
from modules.obras.schemas import ObraRead


@QueryBus.register(GetObraQuery)
async def handle_get_obra(query: GetObraQuery, session: AsyncSession) -> ObraRead:
    obra = await session.get(Obra, query.id)
    if obra is None or obra.usuario_id != query.usuario_id:
        raise NotFoundError(f"Obra {query.id} no encontrada")
    return ObraRead.model_validate(obra, from_attributes=True)
