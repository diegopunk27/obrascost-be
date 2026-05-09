from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.cqrs.query_bus import QueryBus
from modules.obras.models.obra import Obra
from modules.obras.queries.list_obras.list_obras_query import ListObrasQuery
from modules.obras.schemas import ObraRead


@QueryBus.register(ListObrasQuery)
async def handle_list_obras(query: ListObrasQuery, session: AsyncSession) -> list[ObraRead]:
    result = await session.exec(select(Obra).where(Obra.usuario_id == query.usuario_id))
    return [ObraRead.model_validate(o, from_attributes=True) for o in result.all()]
