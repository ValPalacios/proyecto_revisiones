# Proyecto API de Revisiones de Llamadas

Esta es una API construida con Python, FastAPI y PostgreSQL para gestionar revisiones de llamadas ficticias. Permite crear, leer, actualizar y eliminar registros (CRUD).

## Tecnologías
* Python 3.10+
* FastAPI
* PostgreSQL (en Docker)
* Psycopg 3
* Pydantic

## Requisitos Previos
* Tener Docker Desktop instalado y corriendo.
* Tener Git Bash (o terminal Linux).

## Cómo ejecutar el proyecto

1. **Levantar la base de datos:**
   ```bash
   docker compose up -d