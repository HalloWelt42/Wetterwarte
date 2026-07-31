"""Optionales Langzeit-Archiv der gemessenen Radar-Frames (in der Datenbank).

Ist es aktiv, sichert der Recorder je Zyklus die neuesten gemessenen Frames als
gerendertes PNG und entfernt alles aelter als die Aufbewahrungsdauer. Der Radar-
Abspieler kann dann ueber das kurze DWD-Live-Fenster hinaus zurueckblaettern.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from .db import SessionLocal
from .models.einstellung import Einstellung
from .models.radar_archiv import RadarArchivFrame
from .providers import radar

_STD_STUNDEN = 24


async def _lies(schluessel: str, standard: str) -> str:
    async with SessionLocal() as session:
        row = await session.get(Einstellung, schluessel)
        return row.wert if row else standard


async def einstellungen() -> dict:
    aktiv = (await _lies("radar_archiv_aktiv", "0")) == "1"
    try:
        stunden = int(await _lies("radar_archiv_stunden", str(_STD_STUNDEN)))
    except ValueError:
        stunden = _STD_STUNDEN
    return {"aktiv": aktiv, "stunden": max(1, stunden)}


async def setze(aktiv: bool, stunden: int) -> None:
    async with SessionLocal() as session:
        for k, v in (("radar_archiv_aktiv", "1" if aktiv else "0"), ("radar_archiv_stunden", str(max(1, stunden)))):
            row = await session.get(Einstellung, k)
            if row is not None:
                row.wert = v
            else:
                session.add(Einstellung(schluessel=k, wert=v))
        await session.commit()


def _naiv_utc(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(timezone.utc).replace(tzinfo=None)


async def schnappschuss() -> None:
    """Neue gemessene Frames sichern und Altbestand nach Aufbewahrungsdauer entfernen."""
    conf = await einstellungen()
    if not conf["aktiv"]:
        return
    await radar.aktualisiere()  # TTL-gecacht, holt bei Bedarf frische Frames
    gemessen = [f for f in radar.rahmen()["frames"] if f["art"] == "gemessen"]
    if not gemessen:
        return
    async with SessionLocal() as session:
        for f in gemessen:
            if await session.get(RadarArchivFrame, f["id"]) is not None:
                continue
            png = radar.bild(f["id"])
            if png is None:
                continue
            session.add(RadarArchivFrame(frame_id=f["id"], zeit=_naiv_utc(f["zeit"]), png=png))
        grenze = datetime.utcnow() - timedelta(hours=conf["stunden"])
        await session.execute(delete(RadarArchivFrame).where(RadarArchivFrame.zeit < grenze))
        await session.commit()


async def frames_vor(zeit_naiv_utc: datetime) -> list[dict]:
    """Archivierte gemessene Frames, die aelter als der uebergebene Zeitpunkt sind."""
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                select(RadarArchivFrame.frame_id, RadarArchivFrame.zeit)
                .where(RadarArchivFrame.zeit < zeit_naiv_utc)
                .order_by(RadarArchivFrame.zeit)
            )
        ).all()
    return [{"id": r.frame_id, "zeit": r.zeit} for r in rows]


async def bild(frame_id: str) -> bytes | None:
    async with SessionLocal() as session:
        row = await session.get(RadarArchivFrame, frame_id)
        return row.png if row else None


async def statistik() -> dict:
    async with SessionLocal() as session:
        anzahl = (await session.execute(select(func.count()).select_from(RadarArchivFrame))).scalar() or 0
        aeltest = (await session.execute(select(func.min(RadarArchivFrame.zeit)))).scalar()
        neuest = (await session.execute(select(func.max(RadarArchivFrame.zeit)))).scalar()
        bytes_ges = (
            await session.execute(select(func.coalesce(func.sum(func.length(RadarArchivFrame.png)), 0)))
        ).scalar() or 0
    return {
        "anzahl": int(anzahl),
        "aeltest": aeltest.replace(tzinfo=timezone.utc).isoformat() if aeltest else None,
        "neuest": neuest.replace(tzinfo=timezone.utc).isoformat() if neuest else None,
        "bytes": int(bytes_ges),
    }
