from contextlib import asynccontextmanager

from fastapi import FastAPI

import modules.examples.commands.hello.hello_handler  # noqa: F401
import modules.logs.commands.create_log_handler  # noqa: F401
from common.config.settings import get_settings
from common.cqrs.command_bus import CommandBus
from common.cqrs.query_bus import QueryBus
from common.database.session import create_db_and_tables, get_engine, init_engine
from common.exceptions.handlers import register_exception_handlers
from common.logging.logger import setup_logging
from modules.examples.example_router import router as example_router


@asynccontextmanager
async def _lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    if not settings.testing:
        init_engine()
        await create_db_and_tables()
    yield
    if not settings.testing:
        engine = get_engine()
        await engine.dispose()


def create_app() -> FastAPI:
    command_bus = CommandBus()
    query_bus = QueryBus()

    app = FastAPI(
        title="FastAPI CQRS Base",
        version="0.1.0",
        lifespan=_lifespan,
    )
    app.state.command_bus = command_bus
    app.state.query_bus = query_bus

    register_exception_handlers(app, command_bus)

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(example_router)
    return app
