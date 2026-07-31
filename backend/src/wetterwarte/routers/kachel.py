"""Karten-Kacheln ueber den Offline-Cache ausliefern + Speicher-Statistik + Fuell-Bot.

Das Frontend laedt Kacheln ueber /kachel/... (Proxy -> hierher). Treffer kommen von
der Platte, Fehltreffer werden vom Kachel-Dienst geholt und dauerhaft abgelegt.
"""

from fastapi import APIRouter, Body, HTTPException, Response

from .. import kachel_cache
from ..schemas.envelope import wrap

router = APIRouter(prefix="/kachel", tags=["kachel"])


@router.get("/statistik")
async def statistik() -> dict:
    """Belegung des Offline-Caches je Thema (Anbieter) + Fuell-Bot-Zustand."""
    return wrap({**kachel_cache.statistik(), "bot": kachel_cache.zustand()})


@router.get("/schaetzung")
async def schaetzung(anbieter: str = "", zoom_deutschland: int = 8, zoom_heimat: int = 11) -> dict:
    """Grobe Vorab-Schaetzung des Datenvolumens fuer die aktuelle Fuell-Einstellung."""
    liste = [a for a in anbieter.split(",") if a]
    return wrap(await kachel_cache.schaetze(liste, zoom_deutschland, zoom_heimat))


@router.get("/fuellbot")
async def fuellbot_status() -> dict:
    return wrap(kachel_cache.zustand())


@router.post("/fuellbot")
async def fuellbot_start(
    anbieter: list[str] = Body(default=[]),
    zoom_deutschland: int = Body(default=8),
    zoom_heimat: int = Body(default=11),
) -> dict:
    """Fuell-Bot starten: Deutschland (niedrige Zooms) + Wohnort-Umgebung (hoehere)."""
    return wrap(await kachel_cache.starte(anbieter, zoom_deutschland, zoom_heimat))


@router.delete("/fuellbot")
async def fuellbot_stop() -> dict:
    return wrap(kachel_cache.stoppe())


@router.get("/{anbieter}/{z}/{x}/{y}")
async def kachel(anbieter: str, z: int, x: int, y: int) -> Response:
    """Eine Karten-Kachel als PNG (aus dem Cache oder frisch geholt + abgelegt)."""
    bild = await kachel_cache.hole(anbieter, z, x, y)
    if bild is None:
        raise HTTPException(status_code=404, detail="Kachel nicht verfuegbar")
    return Response(
        content=bild,
        media_type=kachel_cache.medientyp(bild),
        headers={"Cache-Control": "public, max-age=604800"},
    )
