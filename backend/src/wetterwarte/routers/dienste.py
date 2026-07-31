"""Dienste-Uebersicht: welche Dienste die Wetterwarte nutzt und ob sie erreichbar sind.

Macht die Abhaengigkeiten transparent (intern / lokal auf dem Pi / extern) mit
Live-Status und Latenz - damit nichts im Verborgenen haengt.
"""

import asyncio
import time

import httpx
from fastapi import APIRouter
from sqlalchemy import text

from .. import cache
from ..config import settings
from ..db import engine
from ..schemas.envelope import wrap

router = APIRouter(prefix="/dienste", tags=["dienste"])

# Statische Beschreibung der Abhaengigkeiten. Reihenfolge = Anzeigereihenfolge.
# art: intern (dieser Stack) | lokal (eigener Pi-Dienst) | extern (Rohdatenquelle)
KATALOG = [
    {"key": "backend", "name": "App-Backend", "rolle": "API + Wetter-Aggregation", "art": "intern", "technik": "FastAPI"},
    {"key": "postgres", "name": "PostgreSQL", "rolle": "Archiv, Layouts, Orte", "art": "intern", "technik": "Postgres 17 (Docker)"},
    {"key": "redis", "name": "Redis", "rolle": "Hot-Cache / Datenfrische", "art": "intern", "technik": "Redis 7 (Docker)"},
    {"key": "osmlocal", "name": "osmlocal", "rolle": "Kartenkacheln Deutschland", "art": "lokal", "technik": "eigener Vektor-/Raster-Render", "ziel": settings.osmlocal_base + "/health"},
    {"key": "lightningmap", "name": "lightningmap", "rolle": "Welt-Kacheln + Live-Blitze", "art": "lokal", "technik": "Kachel-Proxy + Blitzortung", "ziel": settings.lightning_base + "/api/tile/light/0/0/0"},
    {"key": "openmeteo", "name": "Open-Meteo", "rolle": "Vorhersage, Aktuell, Luft, Geokodierung", "art": "extern", "technik": "DWD-ICON u.a.", "ziel": settings.open_meteo_base + "/forecast?latitude=52&longitude=10&current=temperature_2m"},
    {"key": "brightsky", "name": "Bright Sky (DWD)", "rolle": "Amtliche Warnungen", "art": "extern", "technik": "DWD-Aufbereitung", "ziel": settings.bright_sky_base + "/weather?lat=52&lon=10&date=2024-01-01"},
    {"key": "dwd_pollen", "name": "DWD OpenData", "rolle": "Pollenflug", "art": "extern", "technik": "opendata.dwd.de", "ziel": "https://opendata.dwd.de/climate_environment/health/alerts/"},
]

_SCHLUESSEL = "dienste:status"
_TTL = 20  # kurz cachen, damit die Ansicht schnell bleibt und nicht dauernd pingt


async def _ping(ziel: str) -> dict:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
            antwort = await client.get(ziel)
        latenz = round((time.monotonic() - start) * 1000)
        # < 500 = Dienst antwortet (auch 404 heisst: erreichbar).
        return {"status": "ok" if antwort.status_code < 500 else "gestoert", "latenz_ms": latenz, "code": antwort.status_code}
    except Exception:
        return {"status": "offline", "latenz_ms": None, "code": None}


async def _postgres() -> dict:
    start = time.monotonic()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "latenz_ms": round((time.monotonic() - start) * 1000), "code": None}
    except Exception:
        return {"status": "offline", "latenz_ms": None, "code": None}


async def _redis() -> dict:
    start = time.monotonic()
    ok = await cache.erreichbar()
    return {"status": "ok" if ok else "offline", "latenz_ms": round((time.monotonic() - start) * 1000) if ok else None, "code": None}


async def _status_fuer(d: dict) -> dict:
    if d["key"] == "backend":
        return {"status": "ok", "latenz_ms": 0, "code": None}
    if d["key"] == "postgres":
        return await _postgres()
    if d["key"] == "redis":
        return await _redis()
    return await _ping(d["ziel"])


@router.get("")
async def dienste() -> dict:
    gecacht = await cache.hole(_SCHLUESSEL)
    if gecacht is not None:
        return wrap(gecacht)

    stati = await asyncio.gather(*[_status_fuer(d) for d in KATALOG])
    liste = [
        {"key": d["key"], "name": d["name"], "rolle": d["rolle"], "art": d["art"], "technik": d["technik"], **s}
        for d, s in zip(KATALOG, stati)
    ]
    daten = {"dienste": liste, "gesamt": len(liste), "erreichbar": sum(1 for x in liste if x["status"] == "ok")}
    await cache.setze(_SCHLUESSEL, daten, ttl=_TTL)
    return wrap(daten)
