FROM python:3.11-slim

# Evita que Python escriba .pyc y permite ver logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos dependencias primero para aprovechar la caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

# --- Crear un usuario no-root ---
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
# ------------------------------------------------

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]