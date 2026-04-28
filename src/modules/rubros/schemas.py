from pydantic import BaseModel, Field


class RubroCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str = Field(default="", max_length=500)
    costo_referencia_m2: float = Field(ge=0)


class RubroUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)
    costo_referencia_m2: float | None = Field(default=None, ge=0)
    activo: bool | None = None


class RubroRead(BaseModel):
    id: int
    nombre: str
    descripcion: str
    costo_referencia_m2: float
    activo: bool
