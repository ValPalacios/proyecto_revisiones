# Investigación de Docker

## 1. Conceptos Fundamentales

**¿Qué diferencia hay entre imagen, contenedor y máquina virtual?**
- **Imagen:** Es la plantilla de solo lectura con las instrucciones para crear un contenedor (ej. `postgres:15` o la imagen de nuestra API).
- **Contenedor:** Es una instancia en ejecución de una imagen. Es un proceso aislado que comparte el kernel del sistema operativo anfitrión.
- **Máquina Virtual (VM):** Emula un hardware completo y requiere un sistema operativo invitado entero. Consume muchos más recursos (RAM, disco) y tarda más en arrancar que un contenedor.

**¿Qué describe un Dockerfile y qué coordina Compose?**
- **Dockerfile:** Describe *cómo* construir una imagen paso a paso (qué SO base usar, qué dependencias instalar, qué comandos ejecutar).
- **Compose (docker-compose.yaml):** Coordina *múltiples* contenedores. Define cómo se conectan (redes), qué puertos exponen, qué volúmenes usan y en qué orden deben arrancar.

**¿Qué guardan un volumen, un bind mount y la capa escribible?**
- **Volumen:** Datos persistentes gestionados por Docker (ej. `pgdata`). Sobreviven si el contenedor se destruye.
- **Bind mount:** Monta una carpeta de tu PC (host) directamente en el contenedor. Útil para desarrollo (ej. ver cambios de código en tiempo real).
- **Capa escribible:** Todo lo que se escribe dentro del contenedor sin usar volúmenes. Si el contenedor se borra, esta capa se pierde.
- **Persistencia:** Al reiniciar un contenedor, la capa escribible se mantiene. Al recrearlo (por un cambio en Compose) o borrarlo, la capa escribible se pierde, pero los **volúmenes persisten**.

## 2. Redes y Configuración

**¿Cómo se comunican servicios por red y nombre? ¿Por qué `db:5432` vs `localhost:5432`?**
Docker crea una red interna privada. El servicio de base de datos se llama `db` en el Compose. 
- Si la API corre **dentro de Docker**, usa `db:5432` porque Docker resuelve ese nombre al contenedor de la base de datos. Usar `localhost` ahí apuntaría a la propia API.
- Si la API corre en el **host (Windows)**, usa `localhost:5432` porque el puerto está mapeado a tu máquina física.

**¿Qué significan los términos del Compose?**
- `puerto_host:puerto_contenedor`: (ej. `8000:8000`) Mapea el puerto 8000 de tu PC al 8000 del contenedor.
- **Variables de entorno:** Configuraciones externas (ej. `DATABASE_URL`) que el contenedor lee al arrancar.
- **Healthcheck:** Comando que Docker ejecuta periódicamente (ej. `pg_isready`) para saber si el servicio está realmente listo, no solo "encendido".
- **Dependencia de arranque (`depends_on`):** Le dice a Docker que no inicie la API hasta que la base de datos esté "saludable" (`service_healthy`).

## 3. Ventajas y Limitaciones

**¿Qué mejora en este equipo?**
- **Versiones consistentes:** Todos los desarrolladores usan el mismo PostgreSQL 15 y la misma versión de Python, sin importar su SO.
- **Incorporación de compañeros:** Un nuevo compañero solo necesita tener Docker y ejecutar `docker compose up`.
- **Limpieza:** No ensucia la PC con instalaciones nativas de bases de datos.

**¿Qué NO resuelve Docker?**
- **Backups:** No guarda copias de seguridad de la base de datos por sí solo. Si borras el volumen, pierdes los datos.
- **Seguridad por defecto:** Un contenedor no es intrínsecamente seguro; hay que configurarlo (ej. no correr como root).
- **Calidad del código:** Docker no arregla errores de lógica en Python o React.
- **Compatibilidad absoluta:** A veces hay problemas de arquitectura (ej. Apple Silicon M1/M2 vs x86_64).

**¿Cuándo puede no convenir?**
- **Consumo de recursos:** Docker Desktop en Windows/Mac usa una VM ligera por debajo, lo que consume RAM. En equipos con pocos recursos, correr la API de forma nativa puede ser más ligero.
- **Complejidad:** Para un script de 10 líneas, meterlo en Docker puede ser excesivo. No siempre es "más rápido" (la latencia de red interna puede variar).

## 4. Práctica y Validación del Entorno

Para cumplir con la práctica del proyecto, se realizaron las siguientes acciones:

1. **Configuración del Compose:** Se conservó PostgreSQL 15 y el volumen nombrado (`pgdata`). Se creó un archivo `.env.example` sin secretos reales y se ignoró el `.env` real en Git.
2. **Dockerfile de la API:** Se creó un Dockerfile usando `python:3.11-slim`, instalando las dependencias de `requirements.txt` y ejecutando la API con Uvicorn. Se agregó un `.dockerignore` para no copiar entornos virtuales ni el archivo `.env`. Además, se configuró un usuario no-root (`appuser`) por seguridad.
3. **Conexión Interna y Salud:** La API se conecta a la base de datos usando el host `db` y el puerto `5432`. Se agregó un `healthcheck` en el Compose tanto para PostgreSQL como para la API, usando `depends_on: condition: service_healthy` para asegurar el orden de arranque. El endpoint `/salud` verifica la conexión a la base de datos.
4. **Persistencia (Prueba Realizada):** Se levantaron los contenedores, se creó un registro ficticio, se ejecutó `docker compose down` (sin `-v`) y se volvieron a levantar con `docker compose up -d`. Los datos persistieron correctamente.
5. **Advertencia de borrado:** Se documentó en el README que `docker compose down -v` elimina el volumen de datos y no debe usarse para pruebas de persistencia.

## 5. Fuentes Consultadas
- [Docker: ¿Qué es un contenedor?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Docker: Modelo de aplicación Compose](https://docs.docker.com/compose/intro/compose-application-model/)
- [Docker: Dockerfile](https://docs.docker.com/build/concepts/dockerfile/)
- [Docker: Volúmenes](https://docs.docker.com/engine/storage/volumes/)
- [Docker: Redes en Compose](https://docs.docker.com/compose/how-tos/networking/)
- [Docker: Orden de arranque y salud](https://docs.docker.com/compose/how-tos/startup-order/)
- [Docker: Alcance de down](https://docs.docker.com/reference/cli/docker/compose/down/)