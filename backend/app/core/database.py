import psycopg
from backend.app.core.config import settings

def crear_tablas():
    if not settings.DATABASE_URL:
        print("ERROR: La variable DATABASE_URL no está configurada.")
        return
    try:
        with psycopg.connect(settings.DATABASE_URL) as conn:
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