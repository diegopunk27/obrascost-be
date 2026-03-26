from loguru import logger

from common.cqrs.command_bus import CommandBus
from modules.logs.commands.create_log_command import CreateLogCommand


@CommandBus.register(CreateLogCommand)
async def handle_create_log(command: CreateLogCommand) -> None:
    logger.error(
        "Error log (CQRS): {}\n{}",
        command.message,
        command.stack_trace or "(no stack)",
    )
