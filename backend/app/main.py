from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Importamos la función de la BD y los routers
from backend.app.core.database import crear_tablas
from backend.app.routers import llamadas, revisiones, salud

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al arrancar la API
    crear_tablas()
    yield
    # Aquí iría código de apagado (si se necesitara)

app = FastAPI(
    title="API de Revisiones y Llamadas",
    lifespan=lifespan
)

# Registramos los routers
app.include_router(salud.router)
app.include_router(llamadas.router)
app.include_router(revisiones.router)

# Montamos el frontend estático.
# OJO: Como ahora el main está en backend/app/, debemos subir dos niveles para encontrar 'frontend'
import os
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_path = os.path.join(base_dir, "frontend")

app.mount("/ui", StaticFiles(directory=frontend_path, html=True), name="frontend")