# Reporte de Rendimiento (Lentitud reportada)

## 1. Mediciones "Antes" (Frontend Vanilla JS)

**Método de medición:**
Usando las herramientas de desarrollador del navegador (Pestaña Network y Performance) y cronómetro manual durante las pruebas en el entorno local, se midió el flujo de "Crear Llamada" en la interfaz actual (Vanilla JS).

| Acción | Tiempo aproximado | Observaciones |
| :--- | :--- | :--- |
| Petición POST `/llamadas` | ~2 min 15 seg | Tiempo excesivo. Puede deberse a latencia de conexión a PostgreSQL o recarga del servidor Uvicorn. |
| Petición GET `/llamadas` (posterior al POST) | ~2 min 10 seg | El backend tarda en responder y el frontend bloquea la interfaz hasta que termina. |
| DELETE `/llamadas/{id}` | ~1 min 10 seg | Incluso en un caso de error (404), el tiempo de respuesta es extremadamente alto. |

**Prueba de caracterización (Pytest)**
La suite de 4 pruebas automatizadas (que incluyen conexiones a la BD) tardó un total de 130.82 segundos (2 minutos con 10 segundos) en completarse en el entorno local (Windows conectando a Docker). Esto confirma un cuello de botella severo en la latencia de red o en la apertura/cierre de conexiones de Psycopg desde el host hacia el contenedor de PostgreSQL.

**Conclusión "Antes":**
Los tiempos de respuesta del backend (registrados en la red) son inusualmente altos para una API local (superando el minuto de espera). Esto sugiere un cuello de botella en la gestión de conexiones de la base de datos o en la forma en que Uvicorn recarga el proceso. Adicionalmente, en el frontend, tras un POST exitoso, no se usa la entidad devuelta, obligando a una recarga completa con GET y reconstruyendo todo el DOM, lo cual agrava la percepción de lentitud.

## 2. Mediciones "Después" (Pendiente)
Se realizarán cuando se complete la refactorización a React y se optimice la gestión de la base de datos (si es necesario). Se medirá el uso de la entidad devuelta por POST para actualizar el estado local.