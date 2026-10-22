import os
from fastapi import FastAPI
import psycopg
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI()

# Leer las variables del .env
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
dbname = os.getenv("POSTGRES_DB")
host = os.getenv("QA_DB_HOST")
port = os.getenv("QA_DB_PORT")

# Construir la URL de conexión (esto no expone tus contraseñas, solo las usa)
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

def crear_tabla():
    if not user or not password:
        print("ERROR: No se encontraron las variables en el archivo .env")
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
        print("Tabla 'revisiones' verificada/creada con éxito en PostgreSQL.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

@app.on_event("startup")
def startup_event():
    crear_tabla()

@app.get("/salud")
def salud():
    return {"estado": "ok"}