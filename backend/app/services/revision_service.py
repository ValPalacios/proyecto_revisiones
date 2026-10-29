from fastapi import HTTPException
from backend.app.repositories import revision_repo
from backend.app.schemas.revision import RevisionCrear, RevisionActualizar

def crear_revision(revision: RevisionCrear):
    try:
        return revision_repo.crear_revision_db(revision.titulo, revision.nota, revision.estado, revision.llamada_id)
    except Exception as e:
        if "ForeignKeyViolation" in str(type(e)) or "violates foreign key" in str(e):
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def listar_revisiones():
    try:
        return revision_repo.listar_revisiones_db()
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def obtener_revision(id: int):
    try:
        revision = revision_repo.obtener_revision_db(id)
        if not revision:
            raise HTTPException(status_code=404, detail="Revisión no encontrada")
        return revision
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def actualizar_revision(id: int, revision: RevisionActualizar):
    datos = revision.model_dump(exclude_unset=True)
    if not datos:
        return obtener_revision(id)
    try:
        revision_actualizada = revision_repo.actualizar_revision_db(id, datos)
        if not revision_actualizada:
            raise HTTPException(status_code=404, detail="Revisión no encontrada")
        return revision_actualizada
    except HTTPException:
        raise
    except Exception as e:
        if "ForeignKeyViolation" in str(type(e)) or "violates foreign key" in str(e):
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def eliminar_revision(id: int):
    try:
        eliminado = revision_repo.eliminar_revision_db(id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Revisión no encontrada")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")