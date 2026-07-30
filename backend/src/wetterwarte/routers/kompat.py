"""Kompatibilitaets-Schicht: bildet die alte weathercache-API nach.

Damit bestehende Konsumenten (Browser-Extension, FavGrid-Widget) unveraendert
weiterlaufen, wenn Wetterwarte deren Ports uebernimmt. Duenner Adapter ueber die
vorhandenen Provider; Antworten OHNE Envelope (genau wie die alte API).
Endpunkte: /locations, /locations/search, POST /locations,
/weather/current/{id}, /weather/complete/{id}.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .. import ortsdienst
from ..db import get_session
from ..models.ort import Ort
from ..providers import geocoding, luftqualitaet, openmeteo, warnungen

router = APIRouter(tags=["kompat"])


async def _sicher(coro):
    try:
        return await coro
    except Exception:
        return None


def _cond(icon: str | None) -> str:
    """Meteocons-Iconname -> normalisierter Zustands-Schluessel der alten API."""
    if not icon:
        return "cloudy"
    if icon.startswith("clear"):
        return "clear"
    if icon.startswith("partly-cloudy"):
        return "partly_cloudy"
    if icon.startswith("overcast"):
        return "overcast"
    if icon.startswith("fog"):
        return "fog"
    if icon.startswith("drizzle"):
        return "drizzle"
    if icon.startswith("rain"):
        return "rain"
    if icon.startswith("snow"):
        return "snow"
    if icon.startswith("thunderstorms"):
        return "thunderstorm"
    return "cloudy"


def _loc(o: Ort) -> dict:
    return {
        "id": o.slug,
        "name": o.name,
        "latitude": o.lat,
        "longitude": o.lon,
        "country": "DE",
        "country_name": o.land or "Deutschland",
        "region": o.region,
        "timezone": "Europe/Berlin",
        "is_favorite": False,
        "is_home": o.ist_start,
        "display_order": o.reihenfolge,
        "source": "wetterwarte",
        "station_id": None,
    }


def _current_data(a: dict) -> dict:
    sicht = a.get("sicht")
    icon = a.get("icon") or ""
    return {
        "temperature": a["temperatur"],
        "feels_like": a["gefuehlt"],
        "condition": _cond(icon),
        "condition_text": a["zustandText"],
        "weather_code": a.get("weatherCode"),
        "is_day": 0 if "night" in icon else 1,
        "humidity": a["feuchte"],
        "wind_speed": a["wind"],
        "wind_gust": a.get("boeen"),
        "wind_direction": a.get("windGrad"),
        "pressure": a["druck"],
        "visibility": (sicht * 1000 if sicht is not None else None),
        "uv_index": a.get("uv"),
        "clouds": a["bewoelkung"],
        "cloud_cover": a["bewoelkung"],
        "dew_point": a["taupunkt"],
    }


async def _ort(ort_id: str) -> Ort:
    o = await ortsdienst.per_slug(ort_id)
    if o is None:
        raise HTTPException(status_code=404, detail=f"Standort mit ID '{ort_id}' nicht gefunden")
    return o


class LocEingabe(BaseModel):
    name: str
    latitude: float
    longitude: float
    region: str = ""
    country: str = ""
    country_name: str = ""
    timezone: str = ""


@router.get("/locations")
async def locations() -> dict:
    orte = await ortsdienst.alle()
    return {"count": len(orte), "locations": [_loc(o) for o in orte]}


@router.get("/locations/search")
async def locations_search(q: str = "", limit: int = 8) -> dict:
    treffer = await _sicher(geocoding.suche(q, limit)) or []
    return {
        "results": [
            {
                "name": t["name"],
                "region": t["region"],
                "country": "",
                "country_name": t["land"],
                "latitude": t["lat"],
                "longitude": t["lon"],
                "timezone": "Europe/Berlin",
            }
            for t in treffer
        ]
    }


@router.post("/locations")
async def locations_add(eingabe: LocEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    ort = await ortsdienst.anlegen(
        session,
        eingabe.name,
        eingabe.region,
        eingabe.country_name or "Deutschland",
        eingabe.latitude,
        eingabe.longitude,
    )
    return _loc(ort)


@router.get("/weather/current/{ort_id}")
async def weather_current(ort_id: str) -> dict:
    o = await _ort(ort_id)
    basis = await openmeteo.komplett(o.lat, o.lon, o.name, o.region)
    return {"data": _current_data(basis["aktuell"])}


@router.get("/weather/complete/{ort_id}")
async def weather_complete(ort_id: str) -> dict:
    o = await _ort(ort_id)
    basis = await openmeteo.komplett(o.lat, o.lon, o.name, o.region)
    luft, warn = await asyncio.gather(
        _sicher(luftqualitaet.hole(o.lat, o.lon)),
        _sicher(warnungen.hole(o.lat, o.lon)),
    )
    sonne = basis.get("sonne", {})
    days = [
        {
            "weekday": t["kurz"],
            "condition": _cond(t.get("icon")),
            "temperature_max": t["hi"],
            "temperature_min": t["lo"],
            "precipitation_probability": t.get("regen"),
        }
        for t in basis.get("tage", [])
    ]
    hours = [
        {
            "time": s["zeit"],
            "hour": int(s["zeit"]) if str(s["zeit"]).isdigit() else None,
            "temperature": s["temp"],
            "condition": _cond(s.get("icon")),
        }
        for s in basis.get("stunden", [])
    ]
    alerts = [{"headline": w["titel"], "type": w["titel"], "severity": w.get("stufe")} for w in (warn or [])]
    air_quality = {"aqi": luft["aqi"], "aqi_label": luft["label"]} if luft else None
    return {
        "location": _loc(o),
        "current": {
            "data": _current_data(basis["aktuell"]),
            "sun": {"sunrise": sonne.get("aufgang"), "sunset": sonne.get("untergang")},
        },
        "hourly": {"hours": hours},
        "daily": {"days": days},
        "alerts": {"count": len(alerts), "alerts": alerts},
        "air_quality": air_quality,
        "meta": {"source": "wetterwarte"},
    }
