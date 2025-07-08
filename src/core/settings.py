
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "altmur_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "altmur_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "altmur_pass")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    PGADMIN_DEFAULT_EMAIL: str = os.getenv("PGADMIN_DEFAULT_EMAIL", "admin@local.dev")
    PGADMIN_DEFAULT_PASSWORD: str = os.getenv("PGADMIN_DEFAULT_PASSWORD", "admin")

    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    class Config:
        env_file = ".env"

settings = Settings()
