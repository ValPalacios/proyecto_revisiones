import os

class Settings:
    # Leemos la URL de la base de datos desde las variables de entorno
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

settings = Settings()