"""Wetter-Endpunkte - echte Daten ueber gekapselte Provider.

Die Datenherkunft ist gekapselt; ein Wechsel auf den lokal gespiegelten Dienst
oder einen eigenen DWD-Ingester aendert nur den Provider, nicht die Form.
"""

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

import httpx
from fastapi import APIRouter, HTTPException

from .. import cache
from ..orte import ORTE
from ..providers import blitze, luftqualitaet, openmeteo, warnungen
from ..schemas.envelope import wrap

router = APIRouter(prefix="/weather", tags=["weather"])

T = TypeVar("T")


async def _sicher(coro: Awaitable[T]) -> T | None:
    """Zusatzquelle: bei Fehler None statt Abbruch der ganzen Antwort."""
    try:
        return await coro
    except Exception:
        return None


@router.get("/complete/{ort}")
async def complete(ort: str) -> dict:
    """Alles zu einem Ort: aktuell, stuendlich, taeglich, Sonne, Warnungen, Luftqualitaet."""
    o = ORTE.get(ort.lower())
    if o is None:
        raise HTTPException(status_code=404, detail="Ort nicht bekannt")

    schluessel = f"weather:complete:{ort.lower()}"
    gecacht = await cache.hole(schluessel)
    if gecacht is not None:
        return wrap(gecacht)

    try:
        basis = await openmeteo.komplett(o["lat"], o["lon"], o["name"], o["region"])
    except httpx.HTTPError as fehler:
        raise HTTPException(status_code=502, detail=f"Wetterquelle nicht erreichbar: {fehler}") from fehler

    luft, warn, blitz = await asyncio.gather(
        _sicher(luftqualitaet.hole(o["lat"], o["lon"])),
        _sicher(warnungen.hole(o["lat"], o["lon"])),
        _sicher(blitze.hole(o["lat"], o["lon"])),
    )
    basis["luft"] = luft
    basis["warnungen"] = warn or []
    basis["blitze"] = blitz
    await cache.setze(schluessel, basis, ttl=600)
    return wrap(basis)


@router.get("/orte")
async def orte() -> dict:
    """Bekannte Orte (Slug -> Name/Region)."""
    return wrap([{"slug": slug, **werte} for slug, werte in ORTE.items()])
