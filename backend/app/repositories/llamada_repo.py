import psycopg
from backend.app.core.config import settings

def crear_llamada_db(nombre_archivo: str, duracion_seg: int, fecha_llamada) -> dict:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO llamadas (nombre_archivo, duracion_seg, fecha_llamada) 
                VALUES (%s, %s, %s) 
                RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;
                """,
                (nombre_archivo, duracion_seg, fecha_llamada)
            )
            fila = cur.fetchone()
            conn.commit()
            return {
                "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                "fecha_llamada": fila[3], "fecha_creacion": fila[4]
            }

def listar_llamadas_db() -> list:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion FROM llamadas ORDER BY id ASC;")
            filas = cur.fetchall()
            return [
                {
                    "id": f[0], "nombre_archivo": f[1], "duracion_seg": f[2],
                    "fecha_llamada": f[3], "fecha_creacion": f[4]
                } for f in filas
            ]

def obtener_llamada_db(id: int) -> dict | None:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion FROM llamadas WHERE id = %s;", (id,))
            fila = cur.fetchone()
            if not fila:
                return None
            return {
                "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                "fecha_llamada": fila[3], "fecha_creacion": fila[4]
            }

def reemplazar_llamada_db(id: int, nombre_archivo: str, duracion_seg: int, fecha_llamada) -> dict | None:
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE llamadas 
                SET nombre_archivo = %s, duracion_seg = %s, fecha_llamada = %s 
                WHERE id = %s 
                RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;
                """,
                (nombre_archivo, duracion_seg, fecha_llamada, id)
            )
            fila = cur.fetchone()
            conn.commit()
            if not fila:
                return None
            return {
                "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                "fecha_llamada": fila[3], "fecha_creacion": fila[4]
            }

def actualizar_parcial_llamada_db(id: int, datos: dict) -> dict | None:
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
    
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            sql = f"UPDATE llamadas SET {', '.join(campos_actualizar)} WHERE id = %s RETURNING id, nombre_archivo, duracion_seg, fecha_llamada, fecha_creacion;"
            cur.execute(sql, tuple(valores))
            fila = cur.fetchone()
            conn.commit()
            if not fila:
                return None
            return {
                "id": fila[0], "nombre_archivo": fila[1], "duracion_seg": fila[2],
                "fecha_llamada": fila[3], "fecha_creacion": fila[4]
            }

def eliminar_llamada_db(id: int) -> bool:
    try:
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM llamadas WHERE id = %s RETURNING id;", (id,))
                fila = cur.fetchone()
                conn.commit()
                return True if fila else False
    except psycopg.errors.ForeignKeyViolation:
        # El repositorio sí captura el error específico de la BD para avisar al servicio
        raise