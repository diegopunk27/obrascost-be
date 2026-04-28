from datetime import date

from pydantic import BaseModel, Field


class CreateGastoCommand(BaseModel):
    obra_id: int
    rubro_id: int | None = None
    descripcion: str = Field(min_length=3, max_length=300)
    monto: float = Field(gt=0)
    fecha: date
    comprobante_url: str | None = Field(default=None, max_length=500)
