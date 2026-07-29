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

    # Basis-URL fuer Open-Meteo. Vorerst der oeffentliche Dienst (nutzt fuer
    # Deutschland die DWD-ICON-Modelle); spaeter der lokal gespiegelte Dienst.
    open_meteo_base: str = "https://api.open-meteo.com/v1"
    air_quality_base: str = "https://air-quality-api.open-meteo.com/v1"
    # DWD-Warnungen vorerst ueber Bright Sky (DWD-Aufbereitung); spaeter eigener Ingester.
    bright_sky_base: str = "https://api.brightsky.dev"


settings = Settings()
