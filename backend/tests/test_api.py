from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_salud():
    response = client.get("/salud")
    assert response.status_code == 200
    assert response.json() == {"estado": "ok", "base_datos": "disponible"}

def test_crear_llamada_exito():
    payload = {
        "nombre_archivo": "test_automated.wav",
        "duracion_seg": 120,
        "fecha_llamada": "2026-10-22T10:00:00-06:00"
    }
    response = client.post("/llamadas", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre_archivo"] == "test_automated.wav"
    assert data["duracion_seg"] == 120
    assert "id" in data

def test_crear_llamada_fecha_sin_zona_falla():
    payload = {
        "nombre_archivo": "test_falla.wav",
        "duracion_seg": 120,
        "fecha_llamada": "2026-10-22T10:00:00" # Sin zona horaria
    }
    response = client.post("/llamadas", json=payload)
    assert response.status_code == 422

def test_crear_llamada_nombre_vacio_falla():
    payload = {
        "nombre_archivo": "   ",
        "duracion_seg": 120,
        "fecha_llamada": "2026-10-22T10:00:00-06:00"
    }
    response = client.post("/llamadas", json=payload)
    assert response.status_code == 422


def test_patch_llamada_null_falla():
    response = client.get("/llamadas")
    llamada_id = response.json()[0]["id"]
    
    # Intentar enviar null explícito
    response = client.patch(f"/llamadas/{llamada_id}", json={"nombre_archivo": None})
    assert response.status_code == 422

def test_eliminar_llamada_con_revision_409():
    # 1. Crear llamada
    res_llamada = client.post("/llamadas", json={"nombre_archivo": "test_409.wav", "duracion_seg": 10, "fecha_llamada": "2026-10-22T10:00:00-06:00"})
    llamada_id = res_llamada.json()["id"]
    
    # 2. Crear revisión asociada
    client.post("/revisiones", json={"titulo": "test", "llamada_id": llamada_id})
    
    # 3. Intentar borrar la llamada
    res_delete = client.delete(f"/llamadas/{llamada_id}")
    assert res_delete.status_code == 409