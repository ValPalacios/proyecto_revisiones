import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import psycopg
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
dbname = os.getenv("POSTGRES_DB")
host = os.getenv("QA_DB_HOST")
port = os.getenv("QA_DB_PORT")
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

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
    if not user or not password:
        print("⚠️ ERROR: No se encontraron las variables en el archivo .env")
        return
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS revisiones (
                        id SERIAL PRIMARY KEY,
                        titulo VARCHAR(120) NOT NULL,
                        nota VARCHAR(2000) DEFAULT '',
                        estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'revisada')),
                        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        print("✅ Tabla 'revisiones' verificada/creada con éxito en PostgreSQL.")
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")

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