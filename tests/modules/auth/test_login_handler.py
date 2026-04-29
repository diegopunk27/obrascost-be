from unittest.mock import AsyncMock, MagicMock

import bcrypt
import pytest

from common.exceptions.domain import NotFoundError, UnprocessableDomainError
from modules.auth.commands.login.login_command import LoginCommand
from modules.auth.commands.login.login_handler import handle_login, _verify_password
from modules.auth.models.usuario import Usuario


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _make_session(user: Usuario | None) -> AsyncMock:
    """Returns an AsyncMock session whose execute() returns a result with .scalars().first() = user."""
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = user
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session = AsyncMock()
    session.execute.return_value = result_mock
    return session


class TestVerifyPassword:
    def test_password_correcto_retorna_true(self):
        hashed = _hash("secret123")
        assert _verify_password("secret123", hashed) is True

    def test_password_incorrecto_retorna_false(self):
        hashed = _hash("secret123")
        assert _verify_password("wrong", hashed) is False

    def test_password_vacio_no_coincide(self):
        hashed = _hash("secret123")
        assert _verify_password("", hashed) is False


class TestHandleLogin:
    @pytest.mark.asyncio
    async def test_login_exitoso_retorna_token(self):
        user = Usuario(
            id=1,
            email="admin@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Admin",
            role="admin",
            activo=True,
        )
        session = _make_session(user)
        cmd = LoginCommand(email="admin@test.com", password="Admin1234!")

        result = await handle_login(cmd, session)

        assert result.access_token
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_usuario_no_encontrado_lanza_not_found(self):
        session = _make_session(None)
        cmd = LoginCommand(email="noexiste@test.com", password="Admin1234!")

        with pytest.raises(NotFoundError):
            await handle_login(cmd, session)

    @pytest.mark.asyncio
    async def test_password_incorrecto_lanza_not_found(self):
        user = Usuario(
            id=1,
            email="admin@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Admin",
            role="admin",
            activo=True,
        )
        session = _make_session(user)
        cmd = LoginCommand(email="admin@test.com", password="WrongPassword!")

        with pytest.raises(NotFoundError):
            await handle_login(cmd, session)

    @pytest.mark.asyncio
    async def test_usuario_inactivo_lanza_unprocessable(self):
        user = Usuario(
            id=2,
            email="inactivo@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Inactivo",
            role="usuario",
            activo=False,
        )
        session = _make_session(user)
        cmd = LoginCommand(email="inactivo@test.com", password="Admin1234!")

        with pytest.raises(UnprocessableDomainError):
            await handle_login(cmd, session)

    @pytest.mark.asyncio
    async def test_rol_admin_asigna_role_id_1(self):
        from jose import jwt
        from common.config.settings import get_settings

        user = Usuario(
            id=5,
            email="jefe@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Jefe",
            role="admin",
            activo=True,
        )
        session = _make_session(user)
        cmd = LoginCommand(email="jefe@test.com", password="Admin1234!")
        result = await handle_login(cmd, session)

        settings = get_settings()
        payload = jwt.decode(result.access_token, settings.jwt_secret, algorithms=["HS256"])
        assert payload["roleId"] == 1

    @pytest.mark.asyncio
    async def test_rol_usuario_asigna_role_id_2(self):
        from jose import jwt
        from common.config.settings import get_settings

        user = Usuario(
            id=6,
            email="user@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Usuario",
            role="usuario",
            activo=True,
        )
        session = _make_session(user)
        cmd = LoginCommand(email="user@test.com", password="Admin1234!")
        result = await handle_login(cmd, session)

        settings = get_settings()
        payload = jwt.decode(result.access_token, settings.jwt_secret, algorithms=["HS256"])
        assert payload["roleId"] == 2

    @pytest.mark.asyncio
    async def test_sub_en_token_es_string(self):
        from jose import jwt
        from common.config.settings import get_settings

        user = Usuario(
            id=7,
            email="str@test.com",
            password_hash=_hash("Admin1234!"),
            nombre="Test",
            role="admin",
            activo=True,
        )
        session = _make_session(user)
        result = await handle_login(LoginCommand(email="str@test.com", password="Admin1234!"), session)

        settings = get_settings()
        payload = jwt.decode(result.access_token, settings.jwt_secret, algorithms=["HS256"])
        assert isinstance(payload["sub"], str)
        assert payload["sub"] == "7"
