from pydantic import BaseModel, Field


class CreateRubroCommand(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str = Field(default="", max_length=500)
    costo_referencia_m2: float = Field(ge=0)
