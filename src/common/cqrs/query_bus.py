import inspect
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

Handler = Callable[..., Awaitable[Any]]


class QueryBus:
    """Dispatches queries to registered async handlers."""

    _registry: ClassVar[dict[type, Handler]] = {}

    @classmethod
    def register(cls, query_type: type) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            if query_type in cls._registry:
                msg = f"Query handler already registered for {query_type.__name__}"
                raise TypeError(msg)
            cls._registry[query_type] = handler
            return handler

        return decorator

    async def execute(self, query: Any, **kwargs: Any) -> Any:
        query_type = type(query)
        handler = self._registry.get(query_type)
        if handler is None:
            msg = f"No query handler registered for {query_type.__name__}"
            raise KeyError(msg)
        sig = inspect.signature(handler)
        forwarded = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await handler(query, **forwarded)
