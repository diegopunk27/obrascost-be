from datetime import date

from sqlmodel import Field, SQLModel


class Gasto(SQLModel, table=True):
    __tablename__ = "gastos"

    id: int | None = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obras.id", index=True)
    rubro_id: int | None = Field(default=None, foreign_key="rubros.id")
    descripcion: str = Field(max_length=300)
    monto: float = Field(gt=0)
    fecha: date
    comprobante_url: str | None = Field(default=None, max_length=500)
