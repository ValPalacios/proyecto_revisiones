import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import psycopg

app = FastAPI()

# Leemos directamente la variable de entorno. 
# Si no existe, lanzará un error al intentar conectar 
DATABASE_URL = os.getenv("DATABASE_URL")

# --- MODELOS DE VALIDACIÓN (Pydantic) ---
class RevisionCrear(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=120)
    nota: Optional[str] = Field(default="", max_length=2000)
    estado: str = Field(default="pendiente", pattern="^(pendiente|revisada)$")

class RevisionRespuesta(BaseModel):
    id: int
    titulo: str
    nota: str
    estado: str
    fecha_creacion: str

# --- BASE DE DATOS ---
def crear_tabla():
    if not DATABASE_URL:
        print("ERROR: La variable DATABASE_URL no está configurada.")
        return
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # 1. Tabla de llamadas (Nueva)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS llamadas (
                        id SERIAL PRIMARY KEY,
                        nombre_archivo VARCHAR(200) NOT NULL,
                        duracion_seg INTEGER NOT NULL CHECK (duracion_seg BETWEEN 1 AND 86400),
                        fecha_llamada TIMESTAMP WITH TIME ZONE NOT NULL,
                        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 2. Tabla de revisiones (Tuya original)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS revisiones (
                        id SERIAL PRIMARY KEY,
                        titulo VARCHAR(120) NOT NULL,
                        nota VARCHAR(2000) DEFAULT '',
                        estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'revisada')),
                        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # 3. Añadir relación a revisiones (Aditivo, sin borrar datos)
                # Usamos IF NOT EXISTS para que si ya lo aplicamos, no falle al reiniciar.
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

# --- ENDPOINTS ---
@app.get("/salud")
def salud():
    return {"estado": "ok"}

@app.post("/revisiones", status_code=status.HTTP_201_CREATED)
def crear_revision(revision: RevisionCrear):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO revisiones (titulo, nota, estado) 
                    VALUES (%s, %s, %s) 
                    RETURNING id, titulo, nota, estado, fecha_creacion;
                    """,
                    (revision.titulo.strip(), revision.nota, revision.estado)
                )
                resultado = cur.fetchone()
                conn.commit()
                
                return {
                    "id": resultado[0],
                    "titulo": resultado[1],
                    "nota": resultado[2],
                    "estado": resultado[3],
                    "fecha_creacion": resultado[4].isoformat()
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/revisiones", response_model=list[RevisionRespuesta])
def listar_revisiones():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, titulo, nota, estado, fecha_creacion FROM revisiones ORDER BY id ASC;")
                filas = cur.fetchall()
                
                return [
                    {
                        "id": f[0],
                        "titulo": f[1],
                        "nota": f[2],
                        "estado": f[3],
                        "fecha_creacion": f[4].isoformat()
                    } for f in filas
                ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NUEVOS ENDPOINTS ---

@app.get("/revisiones/{id}", response_model=RevisionRespuesta)
def obtener_revision(id: int):
    if id <= 0:
        raise HTTPException(status_code=422, detail="El ID debe ser un entero positivo")
        
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, titulo, nota, estado, fecha_creacion FROM revisiones WHERE id = %s;", (id,))
                fila = cur.fetchone()
                
                if fila is None:
                    raise HTTPException(status_code=404, detail="Revisión no encontrada")
                    
                return {
                    "id": fila[0],
                    "titulo": fila[1],
                    "nota": fila[2],
                    "estado": fila[3],
                    "fecha_creacion": fila[4].isoformat()
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/revisiones/{id}", response_model=RevisionRespuesta)
def actualizar_revision(id: int, revision: dict):
    if id <= 0:
        raise HTTPException(status_code=422, detail="El ID debe ser un entero positivo")
        
    # Validación manual básica para actualizaciones parciales
    campos_actualizar = []
    valores = []
    
    if "titulo" in revision:
        titulo = revision["titulo"]
        if not isinstance(titulo, str) or len(titulo.strip()) < 1 or len(titulo.strip()) > 120:
            raise HTTPException(status_code=422, detail="Título inválido")
        campos_actualizar.append("titulo = %s")
        valores.append(titulo.strip())
        
    if "nota" in revision:
        nota = revision["nota"]
        if not isinstance(nota, str) or len(nota) > 2000:
            raise HTTPException(status_code=422, detail="Nota inválida")
        campos_actualizar.append("nota = %s")
        valores.append(nota)
        
    if "estado" in revision:
        estado = revision["estado"]
        if estado not in ["pendiente", "revisada"]:
            raise HTTPException(status_code=422, detail="Estado inválido")
        campos_actualizar.append("estado = %s")
        valores.append(estado)
        
    # Si no se envió nada, devolvemos el registro tal cual (PATCH vacío)
    if not campos_actualizar:
        return obtener_revision(id)
        
    valores.append(id)
    
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                sql = f"UPDATE revisiones SET {', '.join(campos_actualizar)} WHERE id = %s RETURNING id, titulo, nota, estado, fecha_creacion;"
                cur.execute(sql, tuple(valores))
                fila = cur.fetchone()
                conn.commit()
                
                if fila is None:
                    raise HTTPException(status_code=404, detail="Revisión no encontrada")
                    
                return {
                    "id": fila[0],
                    "titulo": fila[1],
                    "nota": fila[2],
                    "estado": fila[3],
                    "fecha_creacion": fila[4].isoformat()
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/revisiones/{id}", status_code=204)
def eliminar_revision(id: int):
    if id <= 0:
        raise HTTPException(status_code=422, detail="El ID debe ser un entero positivo")
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))