# Proyecto Backend: API de Revisiones y Llamadas Ficticias

## 1. Descripción del Proyecto
Esta es una API profesional construida con **Python**, **FastAPI** y **PostgreSQL** (usando **Psycopg 3** y SQL directo, sin ORM). 
El proyecto inició como un CRUD de "Revisiones" y ha sido extendido para incluir un CRUD completo de "Llamadas Ficticias", estableciendo una relación entre ambas entidades (una llamada puede tener varias revisiones, pero una revisión pertenece a una sola llamada o a ninguna). 

Además, incluye un frontend moderno desarrollado en **React** y un entorno completamente reproducible gracias a **Docker**.

## 2. Tecnologías Utilizadas
* **Python 3.15** (Entorno local).
* **FastAPI** (Framework web backend).
* **Uvicorn** (Servidor ASGI).
* **PostgreSQL 15** (Base de datos, corriendo en Docker).
* **Psycopg 3** (Driver de conexión a PostgreSQL).
* **Pydantic** (Validación de datos).
* **React + Vite** (Frontend moderno).
* **Docker y Docker Compose** (Contenerización de la API y la Base de Datos).
* **Pytest y HTTPX** (Pruebas automatizadas).

## 3. Arquitectura del Proyecto
El backend ha sido refactorizado para separar responsabilidades:
* `backend/app/routers/`: Endpoints y manejo de HTTP.
* `backend/app/schemas/`: Contratos de validación (Pydantic).
* `backend/app/services/`: Reglas de negocio.
* `backend/app/repositories/`: Consultas SQL parametrizadas.
* `backend/app/core/`: Configuración y conexión a la BD.
* `frontend-react/`: Interfaz de usuario desarrollada con React.
* `frontend_vanilla/`: Interfaz anterior en HTML/JS (conservada por referencia).

## 4. Requisitos Previos y Configuración
Para ejecutar este proyecto, asegúrate de tener instalado:
* **Python** y **Git**.
* **Docker** y **Docker Compose** (para la API y la Base de Datos).
* **Node.js** y **npm** (para el frontend en React).

### 4.1 Variables de Entorno
Asegúrate de tener un archivo `.env` en la raíz del proyecto con las credenciales de PostgreSQL (puedes basarte en el archivo `.env.example` proporcionado).

### 4.2 Levantar el entorno con Docker
En la raíz del proyecto, ejecuta:
```bash
docker compose up --build -d
```

*(Esto construirá la API de Python y levantará tanto la base de datos como el servidor FastAPI. Verifica que ambos estén Up con `docker compose ps`)*.

### 4.3 Levantar el Frontend en React
Abre una nueva terminal y dirígete a la carpeta del frontend:

```bash
cd frontend-react
npm install
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.

## 5. Pruebas Automatizadas
El proyecto cuenta con una suite de pruebas unitarias. Con el entorno virtual de Python activado y las dependencias instaladas, ejecuta:

```bash
pytest backend/tests/test_api.py -v
```

## 6. Endpoints Principales
* **POST `/llamadas`**: Crea una llamada.
* **GET `/llamadas`**: Lista todas las llamadas.
* **GET `/llamadas/{id}`**: Obtiene una llamada por ID.
* **PUT `/llamadas/{id}`**: Reemplaza los datos editables de una llamada.
* **PATCH `/llamadas/{id}`**: Actualiza parcialmente una llamada.
* **DELETE `/llamadas/{id}`**: Elimina una llamada (si no tiene revisiones).
* **POST `/revisiones`**: Crea una revisión asociada o no a una llamada.
* **GET `/revisiones`**: Lista revisiones.
* **PATCH `/revisiones/{id}`**: Actualiza parcialmente una revisión.
* **DELETE `/revisiones/{id}`**: Elimina una revisión.
* **GET `/salud`**: Healthcheck (comprueba la disponibilidad de la API y la BD).

## 7. Evidencias y Documentación Adicional
Puedes encontrar la documentación detallada en la carpeta `docs/`:

* `docs/arquitectura.md`: Diagrama y decisiones de diseño.
* `docs/contrato_api.md`: Reglas detalladas de los endpoints.
* `docs/rendimiento.md`: Análisis de rendimiento (Antes vs. Después de Docker).
* `docs/investigacion_docker.md`: Conceptos y práctica de Docker.
* `docs/investigacion_livekit.md`: Análisis funcional para futuras integraciones.

## 8. Advertencia de Datos
Para detener el entorno conservando los datos, usa `docker compose down`.

**NUNCA** uses `docker compose down -v` si quieres conservar los datos, ya que el parámetro `-v` elimina el volumen de PostgreSQL.