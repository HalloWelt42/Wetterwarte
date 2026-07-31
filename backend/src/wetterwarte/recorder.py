"""Hintergrund-Recorder: schreibt ausgewaehlte Messwerte periodisch in die Postgres.

Beim ersten Start wird das Archiv mit der stuendlichen Temperatur der letzten
30 Tage befuellt (Open-Meteo), danach werden alle 10 Minuten die aktuellen
Werte fortgeschrieben. Der Zustand liegt in der Datenbank, nicht im Speicher.
"""

import asyncio
from datetime import datetime

from sqlmodel import select

from . import klima_aggregat, ortsdienst, radar_archiv
from .db import SessionLocal
from .models.aufzeichnung import AufzeichnungOrt
from .models.messwert import Messwert
from .providers import luftqualitaet, openmeteo

INTERVALL_SEKUNDEN = 600
BASIS_VARS = {"temperatur", "feuchte", "wind", "druck"}
LUFT_VARS = {"aqi", "pm2_5", "pm10", "o3", "no2"}
STANDARD_VARS = BASIS_VARS | LUFT_VARS


async def _auswahl() -> dict[str, tuple[bool, set[str]]]:
    """Aufzeichnungs-Auswahl je Ort. Fehlt eine Zeile: aktiv + alle Standard-Variablen."""
    async with SessionLocal() as session:
        rows = (await session.execute(select(AufzeichnungOrt))).scalars().all()
    return {r.ort: (r.aktiv, {v.strip() for v in r.variablen.split(",") if v.strip()}) for r in rows}


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
    auswahl = await _auswahl()
    for o in await ortsdienst.alle():
        aktiv, variablen = auswahl.get(o.slug, (True, set(STANDARD_VARS)))
        if not aktiv or not variablen:
            continue
        werte: dict[str, float] = {}
        # Basiswerte (Temperatur, Feuchte, Wind, Druck) aus dem Wetter-Provider.
        if variablen & BASIS_VARS:
            try:
                daten = await openmeteo.komplett(o.lat, o.lon, o.name, o.region)
                werte.update(daten["aktuell"])
            except Exception:
                pass
        # Luftschadstoffe (AQI, PM2.5, PM10, Ozon, NO2) aus der Luftqualitaet.
        if variablen & LUFT_VARS:
            try:
                luft = await luftqualitaet.hole(o.lat, o.lon)
                if luft:
                    werte.update(luft)
            except Exception:
                pass
        async with SessionLocal() as session:
            for variable in variablen:
                wert = werte.get(variable)
                if wert is not None:
                    try:
                        session.add(Messwert(ort=o.slug, zeit=jetzt, variable=variable, wert=float(wert)))
                    except (TypeError, ValueError):
                        pass
            await session.commit()


async def schleife() -> None:
    # Bestandsorte ohne Zeitzone einmalig nachziehen (fuer Uhr/Sonne/Mond je Ort).
    try:
        await ortsdienst.backfill_zeitzonen()
    except Exception:
        pass
    if await _archiv_leer():
        await _backfill()
        # Nach dem Backfill sofort die Monatsaggregate aufbauen.
        try:
            await klima_aggregat.aktualisiere()
        except Exception:
            pass
    while True:
        try:
            await _schreibe_aktuell()
            # Frisch geschriebene Werte verdichten - nur den laufenden Monat, damit die
            # Zyklus-Kosten unabhaengig von der Archivgroesse konstant bleiben (aeltere
            # Monate aendern sich nicht mehr und wurden bereits frueher aggregiert).
            monatsanfang = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            await klima_aggregat.aktualisiere(seit=monatsanfang)
            # Radar-Frames archivieren (nur wenn im UI aktiviert).
            await radar_archiv.schnappschuss()
        except Exception:
            pass
        await asyncio.sleep(INTERVALL_SEKUNDEN)
