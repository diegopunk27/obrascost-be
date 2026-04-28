from datetime import date

from pydantic import BaseModel, Field


class GastoCreate(BaseModel):
    rubro_id: int | None = None
    descripcion: str = Field(min_length=3, max_length=300)
    monto: float = Field(gt=0)
    fecha: date
    comprobante_url: str | None = Field(default=None, max_length=500)


class GastoUpdate(BaseModel):
    rubro_id: int | None = None
    descripcion: str | None = Field(default=None, min_length=3, max_length=300)
    monto: float | None = Field(default=None, gt=0)
    fecha: date | None = None
    comprobante_url: str | None = Field(default=None, max_length=500)


class GastoRead(BaseModel):
    id: int
    obra_id: int
    rubro_id: int | None
    descripcion: str
    monto: float
    fecha: date
    comprobante_url: str | None
