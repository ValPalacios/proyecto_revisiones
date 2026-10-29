from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import psycopg
from backend.app.core.config import settings

router = APIRouter(tags=["Sistema"])

@router.get("/salud")
def salud():
    # Comprobación de vida del proceso
    try:
        # Comprobación de disponibilidad de la BD
        with psycopg.connect(settings.DATABASE_URL, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"estado": "ok", "base_datos": "disponible"}
    except Exception:
        # Si falla la BD, devolvemos 503
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"estado": "error", "base_datos": "no disponible"}
        )