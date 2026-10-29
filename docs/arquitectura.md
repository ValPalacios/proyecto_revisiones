# Documentación de la Arquitectura Backend

## 1. Decisiones de Arquitectura

Hemos dividido el backend en capas para separar responsabilidades, basándonos en el modelo del proyecto "Transcripción", pero manteniendo el uso de Psycopg 3 y SQL directo (sin ORM).

| Capa | Responsabilidad | Qué NO hace |
| :--- | :--- | :--- |
| **Routers** | Recibir peticiones HTTP, extraer parámetros de ruta y cuerpo, y llamar al servicio correspondiente. | No tiene SQL, no valida reglas de negocio. |
| **Schemas** | Definir los contratos de entrada (validaciones de Pydantic) y salida (respuestas). | No accede a la base de datos. |
| **Services** | Orquestar las reglas de negocio, lanzar excepciones HTTP (404, 409, 422) según corresponda. | No escribe SQL. |
| **Repositories** | Ejecutar consultas SQL parametrizadas y devolver los datos crudos (diccionarios) o `None`. | No lanza errores HTTP, solo errores de base de datos. |
| **Core** | Configurar variables de entorno y gestionar la conexión a la base de datos. | No contiene lógica de negocio. |

## 2. Flujo de una Petición (Ejemplo: POST /llamadas)

1. **React (o Swagger)** envía un JSON con los datos de la llamada.
2. **FastAPI (Router `llamadas.py`)** recibe la petición.
3. **Pydantic (Schema `llamada.py`)** valida que la fecha tenga zona horaria, que los campos sean correctos y rechaza campos extra.
4. **El Router** llama a `llamada_service.crear_llamada()`.
5. **El Servicio (`llamada_service.py`)** recibe los datos validados y llama al repositorio.
6. **El Repositorio (`llamada_repo.py`)** abre una conexión a PostgreSQL, ejecuta el `INSERT` y hace `commit`.
7. **PostgreSQL** devuelve los datos generados (ID, fecha_creacion).
8. **El Repositorio** mapea la fila a un diccionario y lo devuelve al Servicio.
9. **El Servicio** devuelve el diccionario al Router.
10. **El Router** responde con un código `201` y el JSON validado por el Schema de respuesta.

## 3. Diagrama de Flujo

```text
[Cliente] -> (HTTP) -> [Router] -> [Schema (Validación)]
                          |
                          v
                     [Service (Lógica/Negocio)]
                          |
                          v
                     [Repository (SQL)]
                          |
                          v
                   [PostgreSQL (Base de Datos)]