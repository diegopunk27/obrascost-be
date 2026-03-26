from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.auth.jwt_utils import decode_access_token
from common.auth.schemas import TokenPayload, UserSchema

oauth2_scheme = HTTPBearer(auto_error=False)


def _credentials_to_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> UserSchema:
    token = _credentials_to_token(credentials)
    try:
        payload_dict = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc
    payload = TokenPayload.model_validate(payload_dict)
    return UserSchema(
        id=payload.sub,
        email=payload.email,
        role_id=payload.role_id,
        role_name=payload.role_name,
        permissions=payload.permissions,
    )


def require_permissions(*required: str) -> Callable[..., UserSchema]:
    async def dependency(user: UserSchema = Depends(get_current_user)) -> UserSchema:
        if not required:
            return user
        user_perms = user.permissions or []
        if not any(p in user_perms for p in required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
