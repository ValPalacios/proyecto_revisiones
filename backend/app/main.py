from fastapi import FastAPI
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

from fastapi.middleware.cors import CORSMiddleware

# ... (código de lifespan y la creación de app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # El puerto de React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos los routers
app.include_router(salud.router)
app.include_router(llamadas.router)
app.include_router(revisiones.router)
