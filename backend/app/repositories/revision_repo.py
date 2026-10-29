import psycopg
from backend.app.core.config import settings

def crear_revision_db(titulo: str, nota: str, estado: str, llamada_id: int | None) -> dict:
    try:
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO revisiones (titulo, nota, estado, llamada_id) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id, titulo, nota, estado, fecha_creacion, llamada_id;
                    """,
                    (titulo, nota, estado, llamada_id)
                )
                fila = cur.fetchone()
                conn.commit()
                return {
                    "id": fila[0], "titulo": fila[1], "nota": fila[2],
                    "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
                }
    except psycopg.errors.ForeignKeyViolation:
        raise

def listar_revisiones_db() -> list:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, nota, estado, fecha_creacion, llamada_id FROM revisiones ORDER BY id ASC;")
            filas = cur.fetchall()
            return [
                {
                    "id": f[0], "titulo": f[1], "nota": f[2],
                    "estado": f[3], "fecha_creacion": f[4], "llamada_id": f[5]
                } for f in filas
            ]

def obtener_revision_db(id: int) -> dict | None:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, nota, estado, fecha_creacion, llamada_id FROM revisiones WHERE id = %s;", (id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return {
                "id": fila[0], "titulo": fila[1], "nota": fila[2],
                "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
            }

def actualizar_revision_db(id: int, datos: dict) -> dict | None:
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
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                sql = f"UPDATE revisiones SET {', '.join(campos_actualizar)} WHERE id = %s RETURNING id, titulo, nota, estado, fecha_creacion, llamada_id;"
                cur.execute(sql, tuple(valores))
                fila = cur.fetchone()
                conn.commit()
                if not fila:
                    return None
                return {
                    "id": fila[0], "titulo": fila[1], "nota": fila[2],
                    "estado": fila[3], "fecha_creacion": fila[4], "llamada_id": fila[5]
                }
    except psycopg.errors.ForeignKeyViolation:
        raise

def eliminar_revision_db(id: int) -> bool:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM revisiones WHERE id = %s RETURNING id;", (id,))
            fila = cur.fetchone()
            conn.commit()
            return True if fila else False