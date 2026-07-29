"""Wetter-Endpunkte - echte Daten ueber den Open-Meteo-Provider.

Die Datenherkunft ist gekapselt; ein Wechsel auf den lokal gespiegelten Dienst
oder einen eigenen DWD-Ingester aendert nur den Provider, nicht die Form.
"""

import httpx
from fastapi import APIRouter, HTTPException

from ..orte import ORTE
from ..providers import openmeteo
from ..schemas.envelope import wrap

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/complete/{ort}")
async def complete(ort: str) -> dict:
    """Alles zu einem Ort in einer Antwort (aktuell, stuendlich, taeglich, Sonne)."""
    o = ORTE.get(ort.lower())
    if o is None:
        raise HTTPException(status_code=404, detail="Ort nicht bekannt")
    try:
        daten = await openmeteo.komplett(o["lat"], o["lon"], o["name"], o["region"])
    except httpx.HTTPError as fehler:
        raise HTTPException(status_code=502, detail=f"Wetterquelle nicht erreichbar: {fehler}") from fehler
    return wrap(daten)


@router.get("/orte")
async def orte() -> dict:
    """Bekannte Orte (Slug -> Name/Region)."""
    return wrap([{"slug": slug, **werte} for slug, werte in ORTE.items()])
