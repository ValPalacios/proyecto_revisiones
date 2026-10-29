from fastapi import APIRouter, status, Path
from typing import List
from backend.app.schemas.revision import RevisionCrear, RevisionRespuesta, RevisionActualizar
from backend.app.services import revision_service

router = APIRouter(
    prefix="/revisiones",
    tags=["Revisiones"]
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=RevisionRespuesta)
def crear_revision(revision: RevisionCrear):
    return revision_service.crear_revision(revision)

@router.get("", response_model=List[RevisionRespuesta])
def listar_revisiones():
    return revision_service.listar_revisiones()

@router.get("/{id}", response_model=RevisionRespuesta)
def obtener_revision(id: int = Path(..., gt=0)):
    return revision_service.obtener_revision(id)

@router.patch("/{id}", response_model=RevisionRespuesta)
def actualizar_revision(revision: RevisionActualizar, id: int = Path(..., gt=0)):
    return revision_service.actualizar_revision(id, revision)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_revision(id: int = Path(..., gt=0)):
    revision_service.eliminar_revision(id)
    return None