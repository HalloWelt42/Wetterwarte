"""Ortssuche (Geocoding) ueber die Open-Meteo-Geocoding-API.

Liefert zu einem Suchbegriff Kandidaten mit Name, Region (Bundesland), Land und
Koordinaten. Der Nutzer waehlt daraus aus; erst dann wird ein Ort gespeichert.
"""

import httpx

from ..config import settings


async def suche(begriff: str, anzahl: int = 8) -> list[dict]:
    text = (begriff or "").strip()
    if len(text) < 2:
        return []
    params = {"name": text, "count": anzahl, "language": "de", "format": "json"}
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        antwort = await client.get(f"{settings.geocoding_base}/search", params=params)
        antwort.raise_for_status()
        daten = antwort.json()

    treffer = []
    for r in daten.get("results", []):
        treffer.append(
            {
                "name": r["name"],
                "region": r.get("admin1", ""),
                "land": r.get("country", ""),
                "lat": r["latitude"],
                "lon": r["longitude"],
            }
        )
    return treffer
