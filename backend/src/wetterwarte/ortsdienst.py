"""Kleiner Dienst rund um die Ortsliste (fuer Recorder und Wetter-Route).

Die Orte liegen in der Datenbank (per Suche hinzugefuegt). Diese Helfer kapseln
den Zugriff, damit Hintergrund-Recorder und Endpunkte dieselbe Quelle nutzen.
"""

import re

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .db import SessionLocal
from .models.ort import Ort


async def alle() -> list[Ort]:
    async with SessionLocal() as session:
        ergebnis = await session.execute(select(Ort).order_by(Ort.reihenfolge, Ort.name))
        return list(ergebnis.scalars().all())


async def per_slug(slug: str) -> Ort | None:
    async with SessionLocal() as session:
        ergebnis = await session.execute(select(Ort).where(Ort.slug == slug))
        return ergebnis.scalars().first()


def slugify(name: str) -> str:
    s = name.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "ort"


async def backfill_zeitzonen() -> int:
    """Bestandsorte ohne Zeitzone nachtraeglich mit ihrer IANA-Zeitzone fuellen.

    Orte, die vor der Zeitzonen-Unterstuetzung angelegt wurden, haben ein leeres
    Feld; ohne das zeigen Uhr/Sonne/Mond dort die Geraetezeit statt der Ortszeit.
    """
    from .providers import openmeteo

    gefuellt = 0
    async with SessionLocal() as session:
        offen = (
            await session.execute(select(Ort).where((Ort.zeitzone == "") | (Ort.zeitzone.is_(None))))
        ).scalars().all()
        for o in offen:
            try:
                tz = await openmeteo.zeitzone_fuer(o.lat, o.lon)
            except Exception:
                continue
            if tz:
                o.zeitzone = tz
                gefuellt += 1
        if gefuellt:
            await session.commit()
    return gefuellt


async def anlegen(session: AsyncSession, name: str, region: str, land: str, lat: float, lon: float, zeitzone: str = "") -> Ort:
    """Neuen Ort mit eindeutigem Slug anlegen (gemeinsam genutzt von Orte- und Kompat-Router)."""
    basis = slugify(name)
    slug = basis
    n = 2
    while (await session.execute(select(Ort.id).where(Ort.slug == slug))).first() is not None:
        slug = f"{basis}-{n}"
        n += 1
    maxr = (await session.execute(select(func.max(Ort.reihenfolge)))).scalar()
    ort = Ort(slug=slug, name=name, region=region, land=land, lat=lat, lon=lon, zeitzone=zeitzone, reihenfolge=(maxr or 0) + 1)
    session.add(ort)
    await session.commit()
    await session.refresh(ort)
    return ort
