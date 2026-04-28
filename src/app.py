from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import modules.auth.commands.login.login_handler  # noqa: F401
import modules.examples.commands.hello.hello_handler  # noqa: F401
import modules.gastos.commands.create_gasto.create_gasto_handler  # noqa: F401
import modules.gastos.commands.delete_gasto.delete_gasto_handler  # noqa: F401
import modules.gastos.commands.update_gasto.update_gasto_handler  # noqa: F401
import modules.gastos.queries.get_gasto.get_gasto_handler  # noqa: F401
import modules.gastos.queries.list_gastos.list_gastos_handler  # noqa: F401
import modules.logs.commands.create_log_handler  # noqa: F401
import modules.obras.commands.create_obra.create_obra_handler  # noqa: F401
import modules.obras.commands.delete_obra.delete_obra_handler  # noqa: F401
import modules.obras.commands.update_obra.update_obra_handler  # noqa: F401
import modules.obras.queries.get_obra.get_obra_handler  # noqa: F401
import modules.obras.queries.list_obras.list_obras_handler  # noqa: F401
import modules.rubros.commands.create_rubro.create_rubro_handler  # noqa: F401
import modules.rubros.commands.delete_rubro.delete_rubro_handler  # noqa: F401
import modules.rubros.commands.update_rubro.update_rubro_handler  # noqa: F401
import modules.rubros.queries.get_rubro.get_rubro_handler  # noqa: F401
import modules.rubros.queries.list_rubros.list_rubros_handler  # noqa: F401
from common.config.settings import get_settings
from common.cqrs.command_bus import CommandBus
from common.cqrs.query_bus import QueryBus
from common.database.session import create_db_and_tables, get_engine, init_engine
from common.exceptions.handlers import register_exception_handlers
from common.logging.logger import setup_logging
from modules.auth.routers.auth_router import router as auth_router
from modules.examples.example_router import router as example_router
from modules.gastos.routers.gastos_router import router as gastos_router
from modules.obras.routers.obras_router import router as obras_router
from modules.rubros.routers.rubros_router import router as rubros_router


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
        title="ObrasCost API",
        version="1.0.0",
        lifespan=_lifespan,
    )
    app.state.command_bus = command_bus
    app.state.query_bus = query_bus

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app, command_bus)

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(example_router)
    app.include_router(rubros_router)
    app.include_router(obras_router)
    app.include_router(gastos_router)
    return app
