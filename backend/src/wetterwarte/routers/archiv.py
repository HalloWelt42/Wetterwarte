"""Archiv-Endpunkte: Langzeitdaten aus der eigenen PostgreSQL."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..db import get_session
from ..models.messwert import Messwert
from ..schemas.envelope import wrap

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
    ort: str = "koeln",
    variable: str = "temperatur",
    tage: int = 30,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Tagesmittel der gewaehlten Variable ueber den Zeitraum."""
    seit = datetime.now() - timedelta(days=tage)
    tag = func.date(Messwert.zeit)
    stmt = (
        select(tag.label("t"), func.avg(Messwert.wert).label("m"))
        .where(Messwert.ort == ort, Messwert.variable == variable, Messwert.zeit >= seit)
        .group_by(tag)
        .order_by(tag)
    )
    zeilen = (await session.execute(stmt)).all()
    return wrap([{"tag": str(tag_wert), "wert": round(float(mittel), 1)} for tag_wert, mittel in zeilen])
