from fastapi import APIRouter, Depends, status

from common.auth.dependencies import get_current_user
from common.auth.schemas import UserSchema
from common.cqrs.command_bus import CommandBus
from common.cqrs.deps import get_command_bus
from common.database.session import get_session
from modules.auth.commands.login.login_command import LoginCommand
from modules.auth.schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    body: LoginCommand,
    bus: CommandBus = Depends(get_command_bus),
    session=Depends(get_session),
) -> TokenResponse:
    return await bus.execute(body, session=session)


@router.get("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def me(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
    return current_user
