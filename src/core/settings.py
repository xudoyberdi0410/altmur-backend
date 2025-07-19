from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_DB: str = "altmur_db"
    POSTGRES_USER: str = "altmur_user"
    POSTGRES_PASSWORD: str = "altmur_pass"
    DATABASE_URL: str | None = None

    PGADMIN_DEFAULT_EMAIL: str = "admin@local.dev"
    PGADMIN_DEFAULT_PASSWORD: str = "admin"

    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
