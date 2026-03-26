from typing import Any, Protocol, TypeVar

TCommand = TypeVar("TCommand", contravariant=True)
TQuery = TypeVar("TQuery", contravariant=True)
TResult = TypeVar("TResult", covariant=True)


class ICommand(Protocol):
    """Marker protocol for command DTOs (writes)."""


class IQuery(Protocol):
    """Marker protocol for query DTOs (reads)."""


class ICommandHandler(Protocol[TCommand, TResult]):
    async def execute(self, command: TCommand, **kwargs: Any) -> TResult: ...


class IQueryHandler(Protocol[TQuery, TResult]):
    async def execute(self, query: TQuery, **kwargs: Any) -> TResult: ...
