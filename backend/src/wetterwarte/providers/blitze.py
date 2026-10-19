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


def _peilung(la1: float, lo1: float, la2: float, lo2: float) -> float:
    """Richtung vom Ort zum Einschlag in Grad (0 = Nord, im Uhrzeigersinn)."""
    dlon = math.radians(lo2 - lo1)
    y = math.sin(dlon) * math.cos(math.radians(la2))
    x = math.cos(math.radians(la1)) * math.sin(math.radians(la2)) - math.sin(math.radians(la1)) * math.cos(
        math.radians(la2)
    ) * math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def richtung(grad: float) -> str:
    return _RICHTUNGEN[round(grad / 45) % 8]


# Einschläge der letzten Stunde im Umkreis von rund 140 km; mehr kommen dort praktisch nie vor.
_GRENZE = 3000


async def hole(lat: float, lon: float) -> dict:
    """Einschläge der letzten Stunde: Anzahl, die drei neuesten als Text (Desktop) und alle als
    Rohwerte mit Abstand, Peilung und Zeit (Telefon), neueste zuerst."""
    d = 1.3
    params = {"north": lat + d, "south": lat - d, "east": lon + d * 1.6, "west": lon - d * 1.6, "limit": _GRENZE}
    # trust_env=False: keine Proxy-Umleitung fuer den lokalen Pi-Dienst (LAN).
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        antwort = await client.get(f"{settings.lightning_base}/api/strikes", params=params)
        antwort.raise_for_status()
        strikes = antwort.json().get("strikes", [])

    jetzt_ms = time.time() * 1000
    einschlaege = []
    for s in sorted(strikes, key=lambda x: -x.get("t", 0)):
        t = s.get("t", 0)
        if jetzt_ms - t > 3_600_000:
            continue
        einschlaege.append({
            "km": round(_distanz_km(lat, lon, s["lat"], s["lon"]), 1),
            "grad": round(_peilung(lat, lon, s["lat"], s["lon"])),
            "zeit": t,
        })
    liste = [
        {
            "zeit": f"vor {max(0, round((jetzt_ms - e['zeit']) / 60_000))} Min",
            "distanz": f"{round(e['km'])} km {richtung(e['grad'])}",
        }
        for e in einschlaege[:3]
    ]
    return {"anzahl": len(einschlaege), "liste": liste, "einschlaege": einschlaege}
