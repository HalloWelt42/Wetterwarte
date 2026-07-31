"""Konfiguration ueber Umgebungsvariablen (pydantic-settings)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend-Wurzel (.../backend) - fuer projektinterne Standard-Pfade (unabh. vom cwd).
_BACKEND = Path(__file__).resolve().parents[2]


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
    version: str = "0.39.1"

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
    # DWD OpenData: RADOLAN-Radar. RY = gemessene Regenrate (5 min, mm/h, 900x900);
    # RV = RADVOR-Nowcast (Analyse + bis +2 h, mm/h, DE1200). Selbst geholt und gerendert.
    dwd_radar_base: str = "https://opendata.dwd.de/weather/radar"
    # DWD GeoServer (WFS): amtliche Warn-Polygone (zusammengefasst) fuer das Karten-Overlay.
    dwd_warn_wfs: str = "https://maps.dwd.de/geoserver/dwd/ows"
    # Verzeichnis fuer den Offline-Kachel-Cache (themengetrennt je Anbieter). Dev: fest
    # im Backend-Ordner; Prod: Bind-Mount auf die externe SSD (/cache -> /mnt/data/...).
    kachel_cache_dir: str = str(_BACKEND / ".kachelcache")


settings = Settings()
