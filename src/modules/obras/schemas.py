from datetime import date

from pydantic import BaseModel, Field

ESTADOS_VALIDOS = {"borrador", "en_progreso", "pausada", "finalizada", "cancelada"}


class ObraCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=200)
    direccion: str = Field(default="", max_length=300)
    provincia_id: int | None = None
    superficie_m2: float = Field(gt=0)
    fecha_inicio: date
    fecha_fin_estimada: date | None = None
    estado: str = Field(default="borrador")
    presupuesto_inicial: float | None = Field(default=None, ge=0)


class ObraUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=200)
    direccion: str | None = Field(default=None, max_length=300)
    provincia_id: int | None = None
    superficie_m2: float | None = Field(default=None, gt=0)
    fecha_inicio: date | None = None
    fecha_fin_estimada: date | None = None
    estado: str | None = None
    presupuesto_inicial: float | None = Field(default=None, ge=0)


class ObraRead(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    direccion: str
    provincia_id: int | None
    superficie_m2: float
    fecha_inicio: date
    fecha_fin_estimada: date | None
    estado: str
    presupuesto_inicial: float | None


class EstimacionResult(BaseModel):
    total_estimado: float
    desglose_por_rubro: dict[str, float]
    margen_error_pct: float
    fuente: str = "heuristica"
    sugerencia_ia: str | None = None
    ajuste_recomendado_pct: float | None = None
    alertas: list[str] = Field(default_factory=list)
