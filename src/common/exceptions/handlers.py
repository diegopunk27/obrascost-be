from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import ConflictError, NotFoundError, UnprocessableDomainError
from modules.logs.commands.create_log_command import CreateLogCommand


def register_exception_handlers(app: FastAPI, command_bus: CommandBus) -> None:
    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": exc.message},
        )

    @app.exception_handler(UnprocessableDomainError)
    async def unprocessable_domain_handler(
        _request: Request,
        exc: UnprocessableDomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_handler(
        _request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            detail = exc.detail
            message = detail if isinstance(detail, str) else str(detail)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": message},
            )
        if exc.status_code in (
            status.HTTP_409_CONFLICT,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ):
            detail = exc.detail
            message = detail if isinstance(detail, str) else str(detail)
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": message},
            )
        if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            await _log_server_error(command_bus, exc)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An internal server error ocurred, please contact de admins",
                },
            )
        if isinstance(exc.detail, dict | list):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": str(exc.detail)},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled exception: {}", exc)
        await _log_server_error(command_bus, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An internal server error ocurred, please contact de admins"},
        )


async def _log_server_error(command_bus: CommandBus, exc: BaseException) -> None:
    try:
        cmd = CreateLogCommand(message=str(exc), stack_trace=_stack_trace(exc))
        await command_bus.execute(cmd)
    except Exception as log_exc:  # noqa: BLE001
        logger.warning("Failed to dispatch CreateLogCommand: {}", log_exc)


def _stack_trace(exc: BaseException) -> str:
    import traceback

    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
