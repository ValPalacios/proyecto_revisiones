from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

class RevisionCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    titulo: str = Field(..., min_length=1, max_length=120)
    nota: Optional[str] = Field(default="", max_length=2000)
    estado: str = Field(default="pendiente", pattern="^(pendiente|revisada)$")
    llamada_id: Optional[int] = Field(default=None, strict=True, gt=0)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v: str) -> str:
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El título no puede estar vacío ni contener solo espacios")
        return v_limpio

class RevisionActualizar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=120)
    nota: Optional[str] = Field(default=None, max_length=2000)
    estado: Optional[str] = Field(default=None, pattern="^(pendiente|revisada)$")
    llamada_id: Optional[int] = Field(default=None, strict=True, gt=0)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El título no puede estar vacío ni contener solo espacios")
        return v_limpio

class RevisionRespuesta(BaseModel):
    id: int
    titulo: str
    nota: str
    estado: str
    fecha_creacion: datetime
    llamada_id: Optional[int] = None