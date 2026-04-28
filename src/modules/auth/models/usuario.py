from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str
    nombre: str = Field(max_length=100)
    role: str = Field(default="usuario", max_length=20)
    activo: bool = Field(default=True)
