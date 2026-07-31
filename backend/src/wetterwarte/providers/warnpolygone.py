"""Amtliche DWD-Warn-Polygone (zusammengefasst) als GeoJSON fuer das Karten-Overlay.

Quelle: DWD-GeoServer (WFS), Ebene Warnungen_Gemeinden_vereinigt - die bereits
zusammengefassten Warnflaechen (wenige hundert statt tausender Gemeinde-Polygone).
Serverseitig auf die noetigen Eigenschaften getrimmt und kurz gecacht.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from ..config import settings

TTL = timedelta(minutes=3)
_BEHALTE = ("EVENT", "SEVERITY", "HEADLINE", "ONSET", "EXPIRES", "DESCRIPTION", "INSTRUCTION")

_cache: dict = {"geojson": None, "stand": None}
_lock = asyncio.Lock()
_LEER = {"type": "FeatureCollection", "features": []}


async def hole() -> dict:
    """Aktuelle Warn-Polygone als GeoJSON (gecacht). Bei Fehler den letzten Stand."""
    jetzt = datetime.now(timezone.utc)
    if _cache["geojson"] is not None and _cache["stand"] and (jetzt - _cache["stand"]) < TTL:
        return _cache["geojson"]
    async with _lock:
        if _cache["geojson"] is not None and _cache["stand"] and (datetime.now(timezone.utc) - _cache["stand"]) < TTL:
            return _cache["geojson"]
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": "dwd:Warnungen_Gemeinden_vereinigt",
            "outputFormat": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                antwort = await client.get(settings.dwd_warn_wfs, params=params)
                antwort.raise_for_status()
                roh = antwort.json()
        except Exception:
            return _cache["geojson"] or _LEER
        fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": f.get("geometry"),
                    "properties": {k: f.get("properties", {}).get(k) for k in _BEHALTE},
                }
                for f in roh.get("features", [])
                if f.get("geometry")
            ],
        }
        _cache["geojson"] = fc
        _cache["stand"] = datetime.now(timezone.utc)
        return fc
