# Proyecto Backend: API de Revisiones y Llamadas Ficticias

## 1. Descripción del Proyecto
Esta es una API construida con **Python**, **FastAPI** y **PostgreSQL** (usando **Psycopg 3** y SQL directo, sin ORM). 
El proyecto inició como un CRUD de "Revisiones" y ha sido extendido para incluir un CRUD completo de "Llamadas Ficticias", estableciendo una relación entre ambas entidades (una llamada puede tener varias revisiones, pero una revisión pertenece a una sola llamada o a ninguna). 

Además, incluye una interfaz web básica (HTML, CSS y JavaScript vainilla) para gestionar las llamadas de forma visual.

## 2. Tecnologías Utilizadas
*   **Python 3.15** (o la versión que estés usando).
*   **FastAPI** (Framework web).
*   **Uvicorn** (Servidor ASGI).
*   **PostgreSQL 15** (Base de datos, corriendo en Docker).
*   **Psycopg 3** (Driver de conexión a PostgreSQL).
*   **Pydantic** (Validación de datos).
*   **HTML, CSS y JavaScript** (Frontend).

## 3. Requisitos Previos y Configuración
Para ejecutar este proyecto, asegúrate de tener instalado:
*   Python y Git.
*   Docker y Docker Compose (para la base de datos).

### 3.1 Levantar la Base de Datos
En la raíz del proyecto, asegúrate de tener el archivo `docker-compose.yaml` y tu archivo `.env` (con las credenciales locales de práctica). 
Ejecuta:
```bash
docker compose up -d