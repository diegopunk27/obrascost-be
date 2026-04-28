from datetime import date

from sqlmodel import Field, SQLModel


class Obra(SQLModel, table=True):
    __tablename__ = "obras"

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", index=True)
    nombre: str = Field(max_length=200)
    direccion: str = Field(default="", max_length=300)
    provincia_id: int | None = Field(default=None)
    superficie_m2: float = Field(gt=0)
    fecha_inicio: date
    fecha_fin_estimada: date | None = Field(default=None)
    estado: str = Field(default="borrador", max_length=20)
    presupuesto_inicial: float | None = Field(default=None, ge=0)
