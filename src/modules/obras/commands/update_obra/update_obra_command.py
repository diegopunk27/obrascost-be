from datetime import date

from pydantic import BaseModel, Field


class UpdateObraCommand(BaseModel):
    id: int
    nombre: str | None = Field(default=None, min_length=3, max_length=200)
    direccion: str | None = Field(default=None, max_length=300)
    provincia_id: int | None = None
    superficie_m2: float | None = Field(default=None, gt=0)
    fecha_inicio: date | None = None
    fecha_fin_estimada: date | None = None
    estado: str | None = None
    presupuesto_inicial: float | None = Field(default=None, ge=0)
