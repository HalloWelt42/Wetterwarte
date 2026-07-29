"""Luftqualitaet ueber die Open-Meteo-Air-Quality-API."""

import httpx

from ..config import settings


def _label(aqi: int) -> str:
    if aqi <= 20:
        return "Gut"
    if aqi <= 40:
        return "Ordentlich"
    if aqi <= 60:
        return "Mäßig"
    if aqi <= 80:
        return "Schlecht"
    if aqi <= 100:
        return "Sehr schlecht"
    return "Extrem schlecht"


async def hole(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "european_aqi,pm2_5,pm10,ozone,nitrogen_dioxide",
        "timezone": "Europe/Berlin",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.air_quality_base}/air-quality", params=params)
        antwort.raise_for_status()
        c = antwort.json()["current"]

    aqi = round(c["european_aqi"])
    return {
        "aqi": aqi,
        "label": _label(aqi),
        "pm2_5": round(c["pm2_5"]),
        "pm10": round(c["pm10"]),
        "o3": round(c["ozone"]),
        "no2": round(c["nitrogen_dioxide"]),
    }
