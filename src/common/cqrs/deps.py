from fastapi import Request

from common.cqrs.command_bus import CommandBus
from common.cqrs.query_bus import QueryBus


def get_command_bus(request: Request) -> CommandBus:
    return request.app.state.command_bus


def get_query_bus(request: Request) -> QueryBus:
    return request.app.state.query_bus
