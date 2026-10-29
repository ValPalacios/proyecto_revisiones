from fastapi import APIRouter, status, Path
from typing import List
from backend.app.schemas.llamada import LlamadaCrear, LlamadaRespuesta, LlamadaReemplazar, LlamadaActualizarParcial
from backend.app.services import llamada_service

router = APIRouter(
    prefix="/llamadas",
    tags=["Llamadas"]
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=LlamadaRespuesta)
def crear_llamada(llamada: LlamadaCrear):
    return llamada_service.crear_llamada(llamada)

@router.get("", response_model=List[LlamadaRespuesta])
def listar_llamadas():
    return llamada_service.listar_llamadas()

@router.get("/{id}", response_model=LlamadaRespuesta)
def obtener_llamada(id: int = Path(..., gt=0)):
    return llamada_service.obtener_llamada(id)

@router.put("/{id}", response_model=LlamadaRespuesta)
def reemplazar_llamada(llamada: LlamadaReemplazar, id: int = Path(..., gt=0)):
    return llamada_service.reemplazar_llamada(id, llamada)

@router.patch("/{id}", response_model=LlamadaRespuesta)
def actualizar_parcial_llamada(llamada: LlamadaActualizarParcial, id: int = Path(..., gt=0)):
    return llamada_service.actualizar_parcial_llamada(id, llamada)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_llamada(id: int = Path(..., gt=0)):
    llamada_service.eliminar_llamada(id)
    return None