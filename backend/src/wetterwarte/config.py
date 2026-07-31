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
    version: str = "0.25.0"

    # Basis-URL fuer Open-Meteo. Vorerst der oeffentliche Dienst (nutzt fuer
    # Deutschland die DWD-ICON-Modelle); spaeter der lokal gespiegelte Dienst.
    open_meteo_base: str = "https://api.open-meteo.com/v1"
    air_quality_base: str = "https://air-quality-api.open-meteo.com/v1"
    # Ortssuche (Geocoding) - liefert Name, Region, Land und Koordinaten.
    geocoding_base: str = "https://geocoding-api.open-meteo.com/v1"
    # DWD-Warnungen vorerst ueber Bright Sky (DWD-Aufbereitung); spaeter eigener Ingester.
    bright_sky_base: str = "https://api.brightsky.dev"
    # Live-Blitze + Welt-Kacheln vom lokal gehosteten lightningmap-Dienst.
    lightning_base: str = "http://192.168.178.49:8100"
    # Eigener OSM-Vektor-/Raster-Renderdienst (Deutschland) - Backend-API.
    osmlocal_base: str = "http://192.168.178.49:8120"


settings = Settings()
