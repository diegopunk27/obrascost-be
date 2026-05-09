import bcrypt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from common.auth.jwt_utils import create_access_token
from common.cqrs.command_bus import CommandBus
from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.auth.commands.login.login_command import LoginCommand
from modules.auth.models.usuario import Usuario
from modules.auth.schemas import TokenResponse


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


@CommandBus.register(LoginCommand)
async def handle_login(command: LoginCommand, session: AsyncSession) -> TokenResponse:
    result = await session.execute(select(Usuario).where(Usuario.email == command.email))
    user = result.scalars().first()
    if user is None:
        raise NotFoundError("Credenciales inválidas")
    if not user.activo:
        raise UnprocessableDomainError("Usuario inactivo")
    if not _verify_password(command.password, user.password_hash):
        raise NotFoundError("Credenciales inválidas")
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "roleId": 1 if user.role == "admin" else 2,
        "roleName": user.role,
    }
    token = create_access_token(payload)
    return TokenResponse(access_token=token)
