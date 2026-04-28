from datetime import date

from pydantic import BaseModel, Field


class CreateObraCommand(BaseModel):
    usuario_id: int
    nombre: str = Field(min_length=3, max_length=200)
    direccion: str = Field(default="", max_length=300)
    provincia_id: int | None = None
    superficie_m2: float = Field(gt=0)
    fecha_inicio: date
    fecha_fin_estimada: date | None = None
    estado: str = Field(default="borrador")
    presupuesto_inicial: float | None = Field(default=None, ge=0)
