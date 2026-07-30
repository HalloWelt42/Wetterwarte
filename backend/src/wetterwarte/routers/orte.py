"""Endpunkte fuer die Ortsliste: per Suche finden, hinzufuegen, entfernen.

Die Liste ist datengetrieben (Datenbank); es gibt keine fest verdrahteten Orte
mehr im Quellcode - der Nutzer waehlt seine Orte selbst per Suche.
"""

import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..db import get_session
from ..models.ort import Ort
from ..providers import geocoding
from ..schemas.envelope import wrap

router = APIRouter(prefix="/orte", tags=["orte"])


class OrtEingabe(BaseModel):
    name: str
    region: str = ""
    land: str = ""
    lat: float
    lon: float


def _slugify(name: str) -> str:
    s = name.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "ort"


async def _eindeutiger_slug(session: AsyncSession, basis: str) -> str:
    slug = basis
    n = 2
    while (await session.execute(select(Ort.id).where(Ort.slug == slug))).first() is not None:
        slug = f"{basis}-{n}"
        n += 1
    return slug


@router.get("")
async def liste(session: AsyncSession = Depends(get_session)) -> dict:
    ergebnis = await session.execute(select(Ort).order_by(Ort.reihenfolge, Ort.name))
    return wrap([o.model_dump() for o in ergebnis.scalars().all()])


@router.get("/suche")
async def orte_suchen(q: str = "") -> dict:
    """Geocoding-Treffer zu einem Suchbegriff (Name, Region, Land, Koordinaten)."""
    try:
        treffer = await geocoding.suche(q)
    except Exception:
        treffer = []
    return wrap(treffer)


@router.post("")
async def anlegen(eingabe: OrtEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    slug = await _eindeutiger_slug(session, _slugify(eingabe.name))
    maxr = (await session.execute(select(func.max(Ort.reihenfolge)))).scalar()
    ort = Ort(
        slug=slug,
        name=eingabe.name,
        region=eingabe.region,
        land=eingabe.land,
        lat=eingabe.lat,
        lon=eingabe.lon,
        reihenfolge=(maxr or 0) + 1,
    )
    session.add(ort)
    await session.commit()
    await session.refresh(ort)
    return wrap(ort.model_dump())


@router.delete("/{ort_id}")
async def loeschen(ort_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    ort = await session.get(Ort, ort_id)
    if ort is not None:
        await session.delete(ort)
        await session.commit()
    return wrap({"geloescht": True})
