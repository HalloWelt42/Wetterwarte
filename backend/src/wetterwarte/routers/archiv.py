"""Archiv-Endpunkte: Langzeitdaten aus der eigenen PostgreSQL."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .. import ortsdienst
from ..db import get_session
from ..models.messwert import Messwert
from ..schemas.envelope import wrap
from ..zeit import jetzt, zone

router = APIRouter(prefix="/archiv", tags=["archiv"])

# Anzeige-Name + Einheit je aufgezeichneter Variable, in sinnvoller Reihenfolge.
VARIABLEN_META: dict[str, dict[str, str]] = {
    "temperatur": {"label": "Temperatur", "einheit": "°"},
    "feuchte": {"label": "Feuchte", "einheit": " %"},
    "wind": {"label": "Wind", "einheit": " km/h"},
    "druck": {"label": "Luftdruck", "einheit": " hPa"},
    "aqi": {"label": "Luftgüte", "einheit": ""},
    "pm2_5": {"label": "Feinstaub PM2,5", "einheit": " µg/m³"},
    "pm10": {"label": "Feinstaub PM10", "einheit": " µg/m³"},
    "o3": {"label": "Ozon", "einheit": " µg/m³"},
    "no2": {"label": "Stickstoffdioxid", "einheit": " µg/m³"},
}


@router.get("/variablen")
async def variablen(ort: str = "", session: AsyncSession = Depends(get_session)) -> dict:
    """Welche Variablen fuer den Ort tatsaechlich aufgezeichnet sind (mit Label + Einheit)."""
    stmt = select(Messwert.variable).where(Messwert.ort == ort).distinct()
    vorhanden = set((await session.execute(stmt)).scalars().all())
    liste = [
        {"slug": slug, "label": meta["label"], "einheit": meta["einheit"]}
        for slug, meta in VARIABLEN_META.items()
        if slug in vorhanden
    ]
    # Unbekannte (nicht in der Meta-Liste) hinten anhaengen, damit nichts verloren geht.
    for slug in sorted(vorhanden - set(VARIABLEN_META)):
        liste.append({"slug": slug, "label": slug, "einheit": ""})
    return wrap(liste)


@router.get("/verlauf")
async def verlauf(
    ort: str,
    variable: str = "temperatur",
    tage: int = Query(30, ge=1, le=3660),
    aufloesung: str = Query("tag", pattern="^(roh|stunde|tag)$"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Verlauf der Variable über den Zeitraum in der gewünschten Auflösung.

    "roh" zeigt die tatsächlich aufgezeichneten Messpunkte (die neuesten 3000), "stunde" und
    "tag" verdichten in der Ortszeit. Zeiten immer als ISO 8601 mit Versatz."""
    o = await ortsdienst.per_slug(ort.lower())
    if o is None:
        raise HTTPException(status_code=404, detail="Ort nicht bekannt")
    tz = zone(o.zeitzone)
    seit = jetzt() - timedelta(days=tage)
    bedingung = (Messwert.ort == o.slug, Messwert.variable == variable, Messwert.zeit >= seit)
    if aufloesung == "roh":
        stmt = select(Messwert.zeit, Messwert.wert).where(*bedingung).order_by(Messwert.zeit.desc()).limit(3000)
        zeilen = list(reversed((await session.execute(stmt)).all()))
        return wrap([{"tag": zeit.astimezone(tz).isoformat(), "wert": round(float(wert), 1)} for zeit, wert in zeilen])
    # In Ortszeit auf Stunde oder Tag kürzen, dann wieder als Zeitpunkt mit Zone.
    ortszeit = func.timezone(tz.key, Messwert.zeit)
    bucket = func.timezone(tz.key, func.date_trunc("hour" if aufloesung == "stunde" else "day", ortszeit))
    stmt = (
        select(bucket.label("t"), func.avg(Messwert.wert).label("m"))
        .where(*bedingung)
        .group_by(bucket)
        .order_by(bucket)
    )
    zeilen = (await session.execute(stmt)).all()
    return wrap([{"tag": t.astimezone(tz).isoformat(), "wert": round(float(mittel), 1)} for t, mittel in zeilen])
