from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from common.config.settings import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> None:
    global _engine, _session_factory
    settings = get_settings()
    _engine = create_async_engine(
        settings.database_url_async,
        echo=False,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


def get_engine() -> AsyncEngine:
    if _engine is None:
        msg = "Database engine not initialized; call init_engine() during app startup"
        raise RuntimeError(msg)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        msg = "Database session factory not initialized; call init_engine() during app startup"
        raise RuntimeError(msg)
    async with _session_factory() as session:
        yield session


async def create_db_and_tables() -> None:
    """Optional dev helper when SQLMODEL_SYNC is true."""
    settings = get_settings()
    if not settings.sqlmodel_sync:
        return
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
