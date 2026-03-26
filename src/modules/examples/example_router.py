from fastapi import APIRouter, Depends, status

from common.cqrs.command_bus import CommandBus
from common.cqrs.deps import get_command_bus
from modules.examples.commands.hello.hello_command import HelloCommand

router = APIRouter(prefix="/example", tags=["Examples"])


@router.post("/hello", status_code=status.HTTP_201_CREATED)
async def post_hello(
    body: HelloCommand,
    bus: CommandBus = Depends(get_command_bus),
) -> str:
    return await bus.execute(body)
