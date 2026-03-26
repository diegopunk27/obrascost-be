from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import ConflictError
from modules.examples.commands.hello.hello_command import HelloCommand


@CommandBus.register(HelloCommand)
async def handle_hello(command: HelloCommand) -> str:
    if " " in command.name:
        raise ConflictError("The name must be a single name")
    return f"Hola {command.name}!!"
