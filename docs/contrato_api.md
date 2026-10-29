# Contrato de la API de Revisiones y Llamadas

Este documento certifica el comportamiento actual de la API antes de la refactorización arquitectónica.

## 1. Endpoints de Llamadas

| Método | Ruta | Cuerpo (Entrada) | Respuesta Exitosa | Errores esperados |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/llamadas` | `nombre_archivo`, `duracion_seg`, `fecha_llamada` | 201 Created + Objeto completo | 422 (Validación) |
| GET | `/llamadas` | - | 200 OK + Lista de objetos | - |
| GET | `/llamadas/{id}` | - | 200 OK + Objeto | 404 (No existe), 422 (ID inválido) |
| PUT | `/llamadas/{id}` | Los 3 campos editables | 200 OK + Objeto actualizado | 404 (No existe), 422 (Incompleto/Inválido) |
| PATCH | `/llamadas/{id}` | Campos opcionales | 200 OK + Objeto actualizado | 404 (No existe), 422 (Inválido) |
| DELETE | `/llamadas/{id}` | - | 204 No Content | 404 (No existe), 409 (Tiene revisiones) |

## 2. Endpoints de Revisiones

| Método | Ruta | Cuerpo (Entrada) | Respuesta Exitosa | Errores esperados |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/revisiones` | `titulo`, `nota`, `estado`, `llamada_id` | 201 Created + Objeto completo | 404 (Llamada no existe), 422 |
| GET | `/revisiones` | - | 200 OK + Lista | - |
| GET | `/revisiones/{id}` | - | 200 OK + Objeto | 404, 422 |
| PATCH | `/revisiones/{id}` | Campos opcionales | 200 OK + Objeto | 404, 422 |
| DELETE | `/revisiones/{id}` | - | 204 No Content | 404 |

## 3. Endpoints de Sistema
| Método | Ruta | Respuesta |
| :--- | :--- | :--- |
| GET | `/salud` | 200 OK + `{"estado": "ok"}` |