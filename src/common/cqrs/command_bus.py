import inspect
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

Handler = Callable[..., Awaitable[Any]]


class CommandBus:
    """Dispatches commands to registered async handlers (function or callable)."""

    _registry: ClassVar[dict[type, Handler]] = {}

    @classmethod
    def register(cls, command_type: type) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            if command_type in cls._registry:
                msg = f"Command handler already registered for {command_type.__name__}"
                raise TypeError(msg)
            cls._registry[command_type] = handler
            return handler

        return decorator

    async def execute(self, command: Any, **kwargs: Any) -> Any:
        command_type = type(command)
        handler = self._registry.get(command_type)
        if handler is None:
            msg = f"No command handler registered for {command_type.__name__}"
            raise KeyError(msg)
        sig = inspect.signature(handler)
        forwarded = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await handler(command, **forwarded)
