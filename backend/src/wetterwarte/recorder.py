"""Hintergrund-Recorder: schreibt ausgewaehlte Messwerte periodisch in die Postgres.

Beim ersten Start wird das Archiv mit der stuendlichen Temperatur der letzten
30 Tage befuellt (Open-Meteo), danach werden im eingestellten Takt (Standard
10 Minuten) die aktuellen Werte fortgeschrieben. Fuer aussagekraeftige Statistik
- gerade bei kleinschrittigen Einzelwerten - ist ein enger Takt sinnvoll. Der
Takt ist im UI (Aufzeichnungs-Manager) sichtbar und einstellbar; der Zustand
liegt in der Datenbank, nicht im Speicher.
"""

import asyncio
import logging
import time

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import select

from . import klima_aggregat, ortsdienst, radar_archiv, wetterdienst
from .db import SessionLocal
from .models.aufzeichnung import AufzeichnungOrt
from .models.einstellung import Einstellung
from .models.messwert import Messwert
from .providers import openmeteo
from .zeit import jetzt, zone

log = logging.getLogger(__name__)

# Aufzeichnungs-Takt in Minuten: Standard 10, grosszuegig einstellbar. Untere
# Grenze eng genug fuer feine Einzelwerte, obere Grenze noch statistiktauglich.
STD_INTERVALL_MIN = 10
MIN_INTERVALL_MIN = 5
MAX_INTERVALL_MIN = 60
INTERVALL_SCHLUESSEL = "aufzeichnung_intervall_min"

BASIS_VARS = {"temperatur", "feuchte", "wind", "druck"}
LUFT_VARS = {"aqi", "pm2_5", "pm10", "o3", "no2"}
STANDARD_VARS = BASIS_VARS | LUFT_VARS


def _klemme(minuten: int) -> int:
    return max(MIN_INTERVALL_MIN, min(MAX_INTERVALL_MIN, minuten))


async def intervall_min() -> int:
    """Eingestellter Aufzeichnungs-Takt in Minuten (geklemmt auf den erlaubten Bereich)."""
    async with SessionLocal() as session:
        row = await session.get(Einstellung, INTERVALL_SCHLUESSEL)
    try:
        return _klemme(int(row.wert)) if row else STD_INTERVALL_MIN
    except (ValueError, AttributeError):
        return STD_INTERVALL_MIN


async def setze_intervall(minuten: int) -> int:
    """Aufzeichnungs-Takt setzen; gibt den tatsaechlich gespeicherten (geklemmten) Wert zurueck."""
    wert = _klemme(int(minuten))
    async with SessionLocal() as session:
        row = await session.get(Einstellung, INTERVALL_SCHLUESSEL)
        if row is not None:
            row.wert = str(wert)
        else:
            session.add(Einstellung(schluessel=INTERVALL_SCHLUESSEL, wert=str(wert)))
        await session.commit()
    return wert


async def _auswahl() -> dict[str, tuple[bool, set[str]]]:
    """Aufzeichnungs-Auswahl je Ort. Fehlt eine Zeile: aktiv + alle Standard-Variablen."""
    async with SessionLocal() as session:
        rows = (await session.execute(select(AufzeichnungOrt))).scalars().all()
    return {r.ort: (r.aktiv, {v.strip() for v in r.variablen.split(",") if v.strip()}) for r in rows}


async def _archiv_leer() -> bool:
    async with SessionLocal() as session:
        vorhanden = (await session.execute(select(Messwert.id).limit(1))).first()
        return vorhanden is None


async def _speichere(zeilen: list[dict]) -> None:
    """Messwerte schreiben; ein schon vorhandener Wert (gleicher Ort, Größe, Zeit) bleibt."""
    if not zeilen:
        return
    async with SessionLocal() as session:
        ins = pg_insert(Messwert).values(zeilen).on_conflict_do_nothing(index_elements=["ort", "variable", "zeit"])
        await session.execute(ins)
        await session.commit()


async def _backfill() -> None:
    for o in await ortsdienst.alle():
        try:
            reihe = await openmeteo.historie(o.lat, o.lon, tage=30)
        except Exception as fehler:
            log.warning("Nachtrag für %s nicht möglich: %s", o.slug, fehler)
            continue
        await _speichere([{"ort": o.slug, "zeit": zeit, "variable": "temperatur", "wert": wert} for zeit, wert in reihe])


async def _schreibe_aktuell() -> None:
    zeitpunkt = jetzt()
    auswahl = await _auswahl()
    for o in await ortsdienst.alle():
        aktiv, variablen = auswahl.get(o.slug, (True, set(STANDARD_VARS)))
        if not aktiv or not variablen:
            continue
        werte: dict[str, float] = {}
        # Basiswerte (Temperatur, Feuchte, Wind, Druck) ungerundet aus dem gemeinsamen Abruf.
        if variablen & BASIS_VARS:
            basis = await wetterdienst.basis(o)
            if basis.status == "ok" and basis.wert:
                werte.update(openmeteo.messwerte(basis.wert))
        # Luftschadstoffe (AQI, PM2.5, PM10, Ozon, NO2).
        if variablen & LUFT_VARS:
            luft = await wetterdienst.luft(o)
            if luft.status == "ok" and luft.wert:
                werte.update({k: v for k, v in luft.wert.items() if isinstance(v, int | float)})
        zeilen = []
        for variable in variablen:
            wert = werte.get(variable)
            if isinstance(wert, int | float):
                zeilen.append({"ort": o.slug, "zeit": zeitpunkt, "variable": variable, "wert": float(wert)})
        await _speichere(zeilen)


async def _schritt(name: str, aufgabe) -> None:
    """Ein Schritt des Zyklus; scheitert er, laufen die übrigen trotzdem."""
    try:
        await aufgabe()
    except Exception:
        log.exception("Aufzeichnung: Schritt %s fehlgeschlagen", name)


async def _laufende_monate() -> None:
    """Laufenden Monat verdichten, in der Ortszeit jedes Orts (am Monatswechsel können das zwei sein)."""
    monate = {(t.year, t.month) for t in (jetzt().astimezone(zone(o.zeitzone)) for o in await ortsdienst.alle())}
    for monat in sorted(monate):
        await klima_aggregat.aktualisiere(monat=monat)


async def schleife() -> None:
    # Bestandsorte ohne Zeitzone einmalig nachziehen (fuer Uhr/Sonne/Mond je Ort).
    await _schritt("Zeitzonen nachziehen", ortsdienst.backfill_zeitzonen)
    if await _archiv_leer():
        await _schritt("Nachtrag", _backfill)
        await _schritt("Monatsaggregate", klima_aggregat.aktualisiere)
    while True:
        beginn = time.monotonic()
        await _schritt("Messwerte", _schreibe_aktuell)
        # Nur den laufenden Monat verdichten, damit die Kosten nicht mit dem Archiv wachsen.
        await _schritt("Monatsaggregate", _laufende_monate)
        await _schritt("Radar-Archiv", radar_archiv.schnappschuss)
        # Takt jeden Zyklus frisch lesen; die Dauer des Zyklus zählt mit, damit der Takt nicht wandert.
        rest = await intervall_min() * 60 - (time.monotonic() - beginn)
        await asyncio.sleep(max(5.0, rest))
