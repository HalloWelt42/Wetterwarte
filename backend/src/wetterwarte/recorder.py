"""Hintergrund-Recorder: schreibt ausgewaehlte Messwerte periodisch in die Postgres.

Beim ersten Start wird das Archiv mit der stuendlichen Temperatur der letzten
30 Tage befuellt (Open-Meteo), danach werden alle 10 Minuten die aktuellen
Werte fortgeschrieben. Der Zustand liegt in der Datenbank, nicht im Speicher.
"""

import asyncio
from datetime import datetime

from sqlmodel import select

from . import ortsdienst
from .db import SessionLocal
from .models.messwert import Messwert
from .providers import openmeteo

INTERVALL_SEKUNDEN = 600


async def _archiv_leer() -> bool:
    async with SessionLocal() as session:
        vorhanden = (await session.execute(select(Messwert.id).limit(1))).first()
        return vorhanden is None


async def _backfill() -> None:
    for o in await ortsdienst.alle():
        try:
            reihe = await openmeteo.historie(o.lat, o.lon, tage=30)
        except Exception:
            continue
        async with SessionLocal() as session:
            for zeit, wert in reihe:
                session.add(Messwert(ort=o.slug, zeit=datetime.fromisoformat(zeit), variable="temperatur", wert=float(wert)))
            await session.commit()


async def _schreibe_aktuell() -> None:
    jetzt = datetime.now()
    for o in await ortsdienst.alle():
        try:
            daten = await openmeteo.komplett(o.lat, o.lon, o.name, o.region)
        except Exception:
            continue
        a = daten["aktuell"]
        async with SessionLocal() as session:
            for variable in ("temperatur", "feuchte", "wind", "druck"):
                wert = a.get(variable)
                if wert is not None:
                    session.add(Messwert(ort=o.slug, zeit=jetzt, variable=variable, wert=float(wert)))
            await session.commit()


async def schleife() -> None:
    if await _archiv_leer():
        await _backfill()
    while True:
        try:
            await _schreibe_aktuell()
        except Exception:
            pass
        await asyncio.sleep(INTERVALL_SEKUNDEN)
