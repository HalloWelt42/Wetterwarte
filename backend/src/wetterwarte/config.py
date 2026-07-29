"""Konfiguration ueber Umgebungsvariablen (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    # Als str gehalten, damit der +asyncpg-Treiber im Schema erlaubt ist.
    database_url: str = "postgresql+asyncpg://wetterwarte:wetterwarte@localhost:6152/wetterwarte"
    redis_url: str = "redis://localhost:6153/0"
    app_secret: str = "entwicklung"
    version: str = "0.1.0"


settings = Settings()
