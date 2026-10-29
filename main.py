import os
from fastapi import FastAPI, HTTPException, status, Path
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, timezone
import psycopg
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Leemos directamente la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# --- MODELOS DE VALIDACIÓN (Pydantic) ---

# 1. Modelos para Llamadas
class LlamadaCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre_archivo: str = Field(..., min_length=1, max_length=200)
    duracion_seg: int = Field(..., strict=True, ge=1, le=86400)
    fecha_llamada: datetime

    # --- CORRECCIÓN: Validar que la fecha tenga zona horaria y convertir a UTC ---
    @field_validator('fecha_llamada')
    @classmethod
    def validar_fecha_con_zona(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("La fecha debe incluir zona horaria (ej. -06:00 o Z)")
        return v.astimezone(timezone.utc)
    
    # --- CORRECCIÓN: Validar que nombre_archivo no quede vacío tras strip ---
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

# 2. Modelos para Revisiones (Actualizados)
class RevisionCrear(BaseModel):
    # --- CORRECCIÓN: Añadido extra='forbid' ---
    model_config = ConfigDict(extra='forbid')
    titulo: str = Field(..., min_length=1, max_length=120)
    nota: Optional[str] = Field(default="", max_length=2000)
    estado: str = Field(default="pendiente", pattern="^(pendiente|revisada)$")
    llamada_id: Optional[int] = Field(default=None, strict=True, gt=0)

    # --- CORRECCIÓN: Validar título tras strip ---
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

# --- BASE DE DATOS ---
def crear_tabla():
    if not DATABASE_URL:
        print("ERROR: La variable DATABASE_URL no está configurada.")
        return
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # 1. Tabla de llamadas
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS llamadas (
                        id SERIAL PRIMARY KEY,
                        nombre_archivo VARCHAR(200) NOT NULL,
                        duracion_seg INTEGER NOT NULL CHECK (duracion_seg BETWEEN 1 AND 86400),
                        fecha_llamada TIMESTAMP WITH TIME ZONE NOT NULL,
                        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 2. Tabla de revisiones
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS revisiones (
                        id SERIAL PRIMARY KEY,
                        titulo VARCHAR(120) NOT NULL,
                        nota VARCHAR(2000) DEFAULT '',
                        estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'revisada')),
                        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # 3. Añadir relación a revisiones (Aditivo)
                cur.execute("""
                    ALTER TABLE revisiones 
                    ADD COLUMN IF NOT EXISTS llamada_id INTEGER REFERENCES llamadas(id) ON DELETE RESTRICT;
                """)
                conn.commit()
        print("Tablas y relaciones verificadas/creadas con éxito.")
    except Exception as e:
        print(f"Error al conectar o crear las tablas: {e}")

@app.on_event("startup")
def startup_event():
    crear_tabla()

# --- ENDPOINTS LLAMADAS ---

@app.post("/llamadas", status_code=status.HTTP_201_CREATED, response_model=LlamadaRespuesta)
def crear_llamada(llamada: LlamadaCrear):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO llamadas (nombre_archivo, duracion_seg, fecha_llamada) 
                    VALUES (%s, %s, %s) 
                    RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;
                    """,
                    (llamada.nombre_archivo, llamada.duracion_seg, llamada.fecha_llamada)
                )
                fila = cur.fetchone()
                conn.commit()
                return {
                    "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                    "fecha_llamada": fila[3], "fecha_creacion": fila[4]
                }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/llamadas", response_model=List[LlamadaRespuesta])
def listar_llamadas():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion FROM llamadas ORDER BY id ASC;")
                filas = cur.fetchall()
                return [
                    {
                        "id": f[0], "nombre_archivo": f[1], "duracion_seg": f[2],
                        "fecha_llamada": f[3], "fecha_creacion": f[4]
                    } for f in filas
                ]
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# --- CORRECCIÓN: Uso de Path para validar ID > 0 automáticamente (422) ---
@app.get("/llamadas/{id}", response_model=LlamadaRespuesta)
def obtener_llamada(id: int = Path(..., gt=0)):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion FROM llamadas WHERE id = %s;", (id,))
                fila = cur.fetchone()
                if not fila:
                    raise HTTPException(status_code=404, detail="Llamada no encontrada")
                return {
                    "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                    "fecha_llamada": fila[3], "fecha_creacion": fila[4]
                }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/llamadas/{id}", response_model=LlamadaRespuesta)
def reemplazar_llamada(llamada: LlamadaReemplazar, id: int = Path(..., gt=0)):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE llamadas 
                    SET nombre_archivo = %s, duracion_seg = %s, fecha_llamada = %s 
                    WHERE id = %s 
                    RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;
                    """,
                    (llamada.nombre_archivo, llamada.duracion_seg, llamada.fecha_llamada, id)
                )
                fila = cur.fetchone()
                conn.commit()
                if not fila:
                    raise HTTPException(status_code=404, detail="Llamada no encontrada")
                return {
                    "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                    "fecha_llamada": fila[3], "fecha_creacion": fila[4]
                }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.patch("/llamadas/{id}", response_model=LlamadaRespuesta)
def actualizar_parcial_llamada(llamada: LlamadaActualizarParcial, id: int = Path(..., gt=0)):
    datos = llamada.model_dump(exclude_unset=True)
    
    if not datos:
        return obtener_llamada(id)

    campos_actualizar = []
    valores = []
    
    if "nombre_archivo" in datos:
        campos_actualizar.append("nombre_archivo = %s")
        valores.append(datos["nombre_archivo"])
    if "duracion_seg" in datos:
        campos_actualizar.append("duracion_seg = %s")
        valores.append(datos["duracion_seg"])
    if "fecha_llamada" in datos:
        campos_actualizar.append("fecha_llamada = %s")
        valores.append(datos["fecha_llamada"])
        
    valores.append(id)
    
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                sql = f"UPDATE llamadas SET {', '.join(campos_actualizar)} WHERE id = %s RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;"
                cur.execute(sql, tuple(valores))
                fila = cur.fetchone()
                conn.commit()
                if not fila:
                    raise HTTPException(status_code=404, detail="Llamada no encontrada")
                return {
                    "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                    "fecha_llamada": fila[3], "fecha_creacion": fila[4]
                }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/llamadas/{id}", status_code=204)
def eliminar_llamada(id: int = Path(..., gt=0)):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM llamadas WHERE id = %s RETURNING id;", (id,))
                fila = cur.fetchone()
                conn.commit()
                if not fila:
                    raise HTTPException(status_code=404, detail="Llamada no encontrada")
                return None
    except psycopg.errors.ForeignKeyViolation:
        # --- CORRECCIÓN: Rollback explícito y mensaje claro ---
        raise HTTPException(status_code=409, detail="La llamada tiene revisiones asociadas y no puede eliminarse")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# --- ENDPOINTS REVISIONES (ACTUALIZADOS) ---

@app.get("/salud")
def salud():
    return {"estado": "ok"}

@app.post("/revisiones", status_code=status.HTTP_201_CREATED, response_model=RevisionRespuesta)
def crear_revision(revision: RevisionCrear):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO revisiones (titulo, nota, estado, llamada_id) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id, titulo, nota, estado, fecha_creacion, llamada_id;
                    """,
                    (revision.titulo, revision.nota, revision.estado, revision.llamada_id)
                )
                fila = cur.fetchone()
                conn.commit()
                return {
                    "id": fila[0], "titulo": fila[1], "nota": fila[2],
                    "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
                }
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/revisiones", response_model=List[RevisionRespuesta])
def listar_revisiones():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, titulo, nota, estado, fecha_creacion, llamada_id FROM revisiones ORDER BY id ASC;")
                filas = cur.fetchall()
                return [
                    {
                        "id": f[0], "titulo": f[1], "nota": f[2],
                        "estado": f[3], "fecha_creacion": f[4], "llamada_id": f[5]
                    } for f in filas
                ]
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/revisiones/{id}", response_model=RevisionRespuesta)
def obtener_revision(id: int = Path(..., gt=0)):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, titulo, nota, estado, fecha_creacion, llamada_id FROM revisiones WHERE id = %s;", (id,))
                fila = cur.fetchone()
                if fila is None:
                    raise HTTPException(status_code=404, detail="Revisión no encontrada")
                return {
                    "id": fila[0], "titulo": fila[1], "nota": fila[2],
                    "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
                }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.patch("/revisiones/{id}", response_model=RevisionRespuesta)
def actualizar_revision(revision: RevisionActualizar, id: int = Path(..., gt=0)):
    datos = revision.model_dump(exclude_unset=True)
    
    if not datos:
        return obtener_revision(id)

    campos_actualizar = []
    valores = []
    
    if "titulo" in datos:
        campos_actualizar.append("titulo = %s")
        valores.append(datos["titulo"])
    if "nota" in datos:
        campos_actualizar.append("nota = %s")
        valores.append(datos["nota"])
    if "estado" in datos:
        campos_actualizar.append("estado = %s")
        valores.append(datos["estado"])
    if "llamada_id" in datos:
        campos_actualizar.append("llamada_id = %s")
        valores.append(datos["llamada_id"])
        
    valores.append(id)
    
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                sql = f"UPDATE revisiones SET {', '.join(campos_actualizar)} WHERE id = %s RETURNING id, titulo, nota, estado, fecha_creacion, llamada_id;"
                cur.execute(sql, tuple(valores))
                fila = cur.fetchone()
                conn.commit()
                if not fila:
                    raise HTTPException(status_code=404, detail="Revisión no encontrada")
                return {
                    "id": fila[0], "titulo": fila[1], "nota": fila[2],
                    "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
                }
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/revisiones/{id}", status_code=204)
def eliminar_revision(id: int = Path(..., gt=0)):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM revisiones WHERE id = %s RETURNING id;", (id,))
                fila = cur.fetchone()
                conn.commit()
                if fila is None:
                    raise HTTPException(status_code=404, detail="Revisión no encontrada")
                return None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")