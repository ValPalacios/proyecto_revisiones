from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, timezone

class LlamadaCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_archivo: str = Field(..., min_length=1, max_length=200)
    duracion_seg: int = Field(..., strict=True, ge=1, le=86400)
    fecha_llamada: datetime

    @field_validator('fecha_llamada')
    @classmethod
    def validar_fecha_con_zona(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("La fecha debe incluir zona horaria (ej. -06:00 o Z)")
        return v.astimezone(timezone.utc)
    
    @field_validator('nombre_archivo')
    @classmethod
    def validar_nombre_archivo(cls, v: str) -> str:
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El nombre del archivo no puede estar vacío ni contener solo espacios")
        return v_limpio

class LlamadaRespuesta(BaseModel):
    id: int
    nombre_archivo: str
    duracion_seg: int
    fecha_llamada: datetime
    fecha_creacion: datetime

class LlamadaReemplazar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_archivo: str = Field(..., min_length=1, max_length=200)
    duracion_seg: int = Field(..., strict=True, ge=1, le=86400)
    fecha_llamada: datetime

    @field_validator('fecha_llamada')
    @classmethod
    def validar_fecha_con_zona(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("La fecha debe incluir zona horaria (ej. -06:00 o Z)")
        return v.astimezone(timezone.utc)

    @field_validator('nombre_archivo')
    @classmethod
    def validar_nombre_archivo(cls, v: str) -> str:
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El nombre del archivo no puede estar vacío ni contener solo espacios")
        return v_limpio

class LlamadaActualizarParcial(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_archivo: Optional[str] = Field(default=None, min_length=1, max_length=200)
    duracion_seg: Optional[int] = Field(default=None, strict=True, ge=1, le=86400)
    fecha_llamada: Optional[datetime] = None

    @field_validator('fecha_llamada')
    @classmethod
    def validar_fecha_con_zona(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        if v.tzinfo is None:
            raise ValueError("La fecha debe incluir zona horaria (ej. -06:00 o Z)")
        return v.astimezone(timezone.utc)

    @field_validator('nombre_archivo')
    @classmethod
    def validar_nombre_archivo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El nombre del archivo no puede estar vacío ni contener solo espacios")
        return v_limpio