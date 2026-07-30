"""Kleiner Dienst rund um die Ortsliste (fuer Recorder und Wetter-Route).

Die Orte liegen in der Datenbank (per Suche hinzugefuegt). Diese Helfer kapseln
den Zugriff, damit Hintergrund-Recorder und Endpunkte dieselbe Quelle nutzen.
"""

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
