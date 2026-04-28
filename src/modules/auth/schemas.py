from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioRead(BaseModel):
    id: int
    email: str
    nombre: str
    role: str
    activo: bool
