"""Radar-Endpunkte: Frame-Liste (Metadaten) + einzelne gerenderte PNG-Kacheln.

Das eigentliche Holen/Dekodieren/Rendern der RADOLAN-Daten steckt im Provider;
hier wird nur ausgeliefert und gecacht (Frames sind 5 Minuten stabil)."""

from fastapi import APIRouter, HTTPException, Response

from ..providers import radar
from ..schemas.envelope import wrap

router = APIRouter(prefix="/radar", tags=["radar"])


@router.get("/rahmen")
async def rahmen() -> dict:
    """Geordnete Radar-Frames (gemessen + Vorhersage) samt Bild-Eckkoordinaten."""
    try:
        await radar.aktualisiere()
    except Exception:
        pass  # bei Abruffehler den zuletzt bekannten Stand liefern
    return wrap(radar.rahmen())


@router.get("/bild/{fid}.png")
async def bild(fid: str) -> Response:
    """Eine gerenderte Radar-Kachel als PNG (transparent, deckt Deutschland)."""
    png = radar.bild(fid)
    if png is None:
        raise HTTPException(status_code=404, detail="Frame nicht vorhanden")
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "public, max-age=300"})
