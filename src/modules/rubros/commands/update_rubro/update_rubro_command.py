from pydantic import BaseModel, Field


class UpdateRubroCommand(BaseModel):
    id: int
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)
    costo_referencia_m2: float | None = Field(default=None, ge=0)
    activo: bool | None = None
