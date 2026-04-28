from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from common.database.session import get_engine

T = TypeVar("T")


class UnitOfWork:
    """Transactional unit of work (NestJS UnitOfWorkService / withTransaction analogue)."""

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[AsyncSession]:
        engine = get_engine()
        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                yield session

    async def with_transaction(self, fn: Callable[[AsyncSession], Awaitable[T]]) -> T:
        async with self.begin() as session:
            return await fn(session)
