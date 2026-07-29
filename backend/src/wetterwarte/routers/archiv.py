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
