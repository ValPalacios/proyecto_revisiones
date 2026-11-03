# Reporte de Rendimiento: Análisis y Optimización

Este documento detalla la investigación, medición y resolución del problema de lentitud reportado inicialmente en la aplicación.

## 1. Línea Base: Mediciones "Antes"

**Método de medición:**
Se utilizaron las herramientas de desarrollador del navegador (Pestaña Network y Performance) y un cronómetro manual durante las pruebas en el entorno local, midiendo el flujo de "Crear Llamada" con la interfaz original (Vanilla JS) y la API corriendo de forma nativa en Windows.

| Acción | Tiempo aproximado | Observaciones |
| :--- | :--- | :--- |
| Petición POST `/llamadas` | ~2 min 15 seg | Tiempo excesivo. Latencia de conexión a PostgreSQL. |
| Petición GET `/llamadas` (posterior al POST) | ~2 min 10 seg | El frontend bloqueaba la interfaz esperando la recarga completa. |
| DELETE `/llamadas/{id}` | ~1 min 10 seg | Incluso en casos de error (404), el tiempo era extremadamente alto. |

**Prueba de caracterización (Pytest):**
Al ejecutar la suite de 4 pruebas automatizadas (que realizan conexiones reales a la BD), el tiempo total fue de **130.82 segundos (2 minutos con 10 segundos)**. Esto confirmó empíricamente un cuello de botella severo en la latencia de red y en la apertura/cierre de conexiones de Psycopg desde el host (Windows) hacia el contenedor de PostgreSQL.

**Conclusión "Antes":**
La lentitud no era un problema de lógica de negocio, sino de infraestructura y del manejo del estado en el frontend. Las peticiones desde Windows a Docker tardaban minutos, y la interfaz en Vanilla JS no aprovechaba la entidad devuelta por el POST, obligando a hacer un GET adicional y reconstruyendo todo el DOM, lo que agravaba la mala experiencia de usuario.

## 2. Acciones de Optimización Implementadas

Para resolver el cuello de botella, se aplicaron dos soluciones arquitectónicas:

1. **Infraestructura (Docker):** Se contenerizó la API de FastAPI. Ahora la API y PostgreSQL se comunican internamente a través de la red privada de Docker (`db:5432`), eliminando la latencia de red del sistema anfitrión. El tiempo de respuesta pasó de minutos a milisegundos.
2. **Frontend (React):** Se migró la interfaz a React. En lugar de hacer una petición GET completa (`recargar()`) después de crear o editar un registro, el componente captura la entidad devuelta por la respuesta del servidor (`response.json()`) y actualiza el estado local (`setLlamadas`).

## 3. Mediciones "Después" y Resultados

| Acción | Tiempo aproximado | Observaciones |
| :--- | :--- | :--- |
| Petición POST `/llamadas` (React + Docker) | ~10 ms | La API responde casi instantáneamente desde Docker. |
| Actualización de la vista (React) | ~5 ms | React actualiza el DOM virtual de forma eficiente sin recargar toda la página. |
| **Pruebas Automatizadas (Pytest)** | **~2 segundos** | La suite completa de pruebas pasa en una fracción del tiempo original. |

**Conclusión Final:**
La combinación de contenerizar la API y optimizar el manejo del estado en React **eliminó por completo la lentitud reportada**. La aplicación ahora responde en milisegundos, ofreciendo una experiencia de usuario fluida y un entorno de desarrollo reproducible.