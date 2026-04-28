from sqlmodel import Field, SQLModel


class Rubro(SQLModel, table=True):
    __tablename__ = "rubros"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: str = Field(default="", max_length=500)
    costo_referencia_m2: float = Field(ge=0)
    activo: bool = Field(default=True)
