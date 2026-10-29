from fastapi import HTTPException
from backend.app.repositories import llamada_repo
from backend.app.schemas.llamada import LlamadaCrear, LlamadaReemplazar, LlamadaActualizarParcial

def crear_llamada(llamada: LlamadaCrear):
    try:
        return llamada_repo.crear_llamada_db(llamada.nombre_archivo, llamada.duracion_seg, llamada.fecha_llamada)
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def listar_llamadas():
    try:
        return llamada_repo.listar_llamadas_db()
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def obtener_llamada(id: int):
    try:
        llamada = llamada_repo.obtener_llamada_db(id)
        if not llamada:
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        return llamada
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def reemplazar_llamada(id: int, llamada: LlamadaReemplazar):
    try:
        llamada_actualizada = llamada_repo.reemplazar_llamada_db(id, llamada.nombre_archivo, llamada.duracion_seg, llamada.fecha_llamada)
        if not llamada_actualizada:
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        return llamada_actualizada
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def actualizar_parcial_llamada(id: int, llamada: LlamadaActualizarParcial):
    datos = llamada.model_dump(exclude_unset=True)
    if not datos:
        return obtener_llamada(id)
    try:
        llamada_actualizada = llamada_repo.actualizar_parcial_llamada_db(id, datos)
        if not llamada_actualizada:
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        return llamada_actualizada
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def eliminar_llamada(id: int):
    try:
        eliminado = llamada_repo.eliminar_llamada_db(id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        # Capturamos si el repo lanzó el error por la llave foránea
        if "ForeignKeyViolation" in str(type(e)) or "violates foreign key" in str(e):
            raise HTTPException(status_code=409, detail="La llamada tiene revisiones asociadas y no puede eliminarse")
        raise HTTPException(status_code=500, detail="Error interno del servidor")