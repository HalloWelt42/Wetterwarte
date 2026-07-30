"""Live-Blitze vom lokal gehosteten lightningmap-Dienst (Blitzortung.org)."""

import math
import time

import httpx

from ..config import settings

_RICHTUNGEN = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]


def _distanz_km(la1: float, lo1: float, la2: float, lo2: float) -> float:
    r = 6371
    p1, p2 = math.radians(la1), math.radians(la2)
    dp = math.radians(la2 - la1)
    dl = math.radians(lo2 - lo1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


def _richtung(la1: float, lo1: float, la2: float, lo2: float) -> str:
    dlon = math.radians(lo2 - lo1)
    y = math.sin(dlon) * math.cos(math.radians(la2))
    x = math.cos(math.radians(la1)) * math.sin(math.radians(la2)) - math.sin(math.radians(la1)) * math.cos(
        math.radians(la2)
    ) * math.cos(dlon)
    grad = (math.degrees(math.atan2(y, x)) + 360) % 360
    return _RICHTUNGEN[round(grad / 45) % 8]


async def hole(lat: float, lon: float) -> dict:
    d = 1.3
    params = {"north": lat + d, "south": lat - d, "east": lon + d * 1.6, "west": lon - d * 1.6, "limit": 500}
    # trust_env=False: keine Proxy-Umleitung fuer den lokalen Pi-Dienst (LAN).
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        antwort = await client.get(f"{settings.lightning_base}/api/strikes", params=params)
        antwort.raise_for_status()
        strikes = antwort.json().get("strikes", [])

    jetzt = time.time() * 1000
    letzte_stunde = [s for s in strikes if jetzt - s.get("t", 0) <= 3_600_000]
    liste = []
    for s in sorted(strikes, key=lambda x: -x.get("t", 0))[:3]:
        dist = round(_distanz_km(lat, lon, s["lat"], s["lon"]))
        minuten = max(0, round((jetzt - s.get("t", jetzt)) / 60_000))
        liste.append({
            "zeit": f"vor {minuten} Min",
            "distanz": f"{dist} km {_richtung(lat, lon, s['lat'], s['lon'])}",
        })
    return {"anzahl": len(letzte_stunde), "liste": liste}
