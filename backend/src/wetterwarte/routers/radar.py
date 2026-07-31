"""Radar-Endpunkte: Frame-Liste (Metadaten) + einzelne gerenderte PNG-Kacheln.

Das eigentliche Holen/Dekodieren/Rendern der RADOLAN-Daten steckt im Provider;
hier wird nur ausgeliefert und gecacht. Optional wird das DB-Archiv (historische
gemessene Frames) vorangestellt, damit der Abspieler weiter zurueckblaettern kann.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException, Response

from .. import radar_archiv
from ..providers import radar
from ..schemas.envelope import wrap

router = APIRouter(prefix="/radar", tags=["radar"])


@router.get("/rahmen")
async def rahmen() -> dict:
    """Geordnete Radar-Frames (Archiv + gemessen + Vorhersage) samt Bild-Eckkoordinaten."""
    try:
        await radar.aktualisiere()
    except Exception:
        pass  # bei Abruffehler den zuletzt bekannten Stand liefern
    r = radar.rahmen()
    try:
        conf = await radar_archiv.einstellungen()
        gemessen = [f for f in r["frames"] if f["art"] == "gemessen"]
        if conf["aktiv"] and gemessen:
            bezug = max(datetime.fromisoformat(f["zeit"]) for f in gemessen)
            fruehest = min(datetime.fromisoformat(f["zeit"]) for f in gemessen)
            arch = await radar_archiv.frames_vor(fruehest.astimezone(timezone.utc).replace(tzinfo=None))
            vorher = []
            for a in arch:
                zt = a["zeit"].replace(tzinfo=timezone.utc)
                vorher.append(
                    {
                        "id": a["id"],
                        "zeit": zt.isoformat(),
                        "offset": round((zt - bezug).total_seconds() / 60),
                        "art": "gemessen",
                    }
                )
            r = {**r, "frames": vorher + r["frames"]}
    except Exception:
        pass
    return wrap(r)


@router.get("/archiv")
async def archiv_status() -> dict:
    """Status des Radar-Archivs: aktiv, Aufbewahrungsdauer, Anzahl, Zeitraum, Speicher."""
    conf = await radar_archiv.einstellungen()
    stat = await radar_archiv.statistik()
    return wrap({**conf, **stat})


@router.put("/archiv")
async def archiv_setzen(aktiv: bool = Body(...), stunden: int = Body(24)) -> dict:
    """Radar-Archiv ein-/ausschalten und die Aufbewahrungsdauer (Stunden) setzen."""
    await radar_archiv.setze(aktiv, stunden)
    conf = await radar_archiv.einstellungen()
    stat = await radar_archiv.statistik()
    return wrap({**conf, **stat})


@router.get("/bild/{fid}.png")
async def bild(fid: str) -> Response:
    """Eine gerenderte Radar-Kachel als PNG (Live-Cache, sonst aus dem Archiv)."""
    png = radar.bild(fid)
    if png is None:
        png = await radar_archiv.bild(fid)
    if png is None:
        raise HTTPException(status_code=404, detail="Frame nicht vorhanden")
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "public, max-age=300"})
