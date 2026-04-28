from datetime import date

from pydantic import BaseModel, Field


class UpdateGastoCommand(BaseModel):
    id: int
    obra_id: int
    rubro_id: int | None = None
    descripcion: str | None = Field(default=None, min_length=3, max_length=300)
    monto: float | None = Field(default=None, gt=0)
    fecha: date | None = None
    comprobante_url: str | None = Field(default=None, max_length=500)
