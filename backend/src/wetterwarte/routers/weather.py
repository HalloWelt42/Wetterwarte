"""Wetter-Endpunkte - echte Daten ueber gekapselte Provider.

Die Datenherkunft ist gekapselt; ein Wechsel auf den lokal gespiegelten Dienst
oder einen eigenen DWD-Ingester aendert nur den Provider, nicht die Form.

Datenfrische pro Bereich: zeitkritische Daten (Warnungen, Blitze) werden kurz
gecacht, traege Daten (Vorhersage, Luft, Pollen) laenger. Das Frontend fragt
jeden Bereich in seinem eigenen Takt ab (siehe wetter.svelte.ts).
"""

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import TypeVar

import httpx
from fastapi import APIRouter, HTTPException

from .. import cache, klima_aggregat, ortsdienst
from ..db import SessionLocal
from ..models.klima import KlimaNormale
from ..providers import blitze, klima, luftqualitaet, openmeteo, pollen_dwd, warnpolygone, warnungen
from ..schemas.envelope import wrap

router = APIRouter(prefix="/wetter", tags=["wetter"])

# Kurze Monatsnamen fuer die Diagramm-Beschriftung.
MONATE_KURZ = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

T = TypeVar("T")

# Cache-Stufen (Sekunden) je nach Zeitkritikalitaet der Quelle.
TTL_BASIS = 300     # aktuell/stuendlich/taeglich/Sonne - ~5 min
TTL_WARN = 120      # Warnungen - zeitkritisch, ~2 min
TTL_BLITZE = 60     # Blitze - zeitkritisch, ~1 min
TTL_LUFT = 900      # Luftqualitaet - traege, 15 min
TTL_POLLEN = 3600   # Pollen - sehr traege, 1 h


# Ein Lock je Cache-Schluessel: verhindert, dass bei Cache-Miss mehrere gleichzeitige
# Anfragen denselben Upstream-Abruf parallel ausloesen (Single-Flight / kein Thundering Herd).
_locks: dict[str, asyncio.Lock] = {}


def _lock(schluessel: str) -> asyncio.Lock:
    sperre = _locks.get(schluessel)
    if sperre is None:
        sperre = _locks[schluessel] = asyncio.Lock()
    return sperre


async def _sicher(coro: Awaitable[T]) -> T | None:
    """Zusatzquelle: bei Fehler None statt Abbruch der ganzen Antwort."""
    try:
        return await coro
    except Exception:
        return None


async def _ort(ort: str):
    o = await ortsdienst.per_slug(ort.lower())
    if o is None:
        raise HTTPException(status_code=404, detail="Ort nicht bekannt")
    return o


async def _basis(o) -> dict:
    """Aktuell + stuendlich + taeglich + Sonne (eine Open-Meteo-Abfrage), gecacht."""
    schluessel = f"weather:basis:{o.slug}"
    gecacht = await cache.hole(schluessel)
    if gecacht is not None:
        return gecacht
    async with _lock(schluessel):
        gecacht = await cache.hole(schluessel)  # ein paralleler Task hat evtl. schon gefuellt
        if gecacht is not None:
            return gecacht
        try:
            b = await openmeteo.komplett(o.lat, o.lon, o.name, o.region)
        except httpx.HTTPError as fehler:
            raise HTTPException(status_code=502, detail=f"Wetterquelle nicht erreichbar: {fehler}") from fehler
        await cache.setze(schluessel, b, ttl=TTL_BASIS)
        return b


async def _gecacht(schluessel: str, ttl: int, quelle: Callable[[], Awaitable[T]], ersatz: T) -> T:
    """Zusatzbereich mit eigener Cache-Stufe. Bei Fehler den Ersatz liefern und
    NICHT cachen, damit der naechste Takt es erneut versucht."""
    gecacht = await cache.hole(schluessel)
    if gecacht is not None:
        return gecacht
    async with _lock(schluessel):
        gecacht = await cache.hole(schluessel)  # ein paralleler Task hat evtl. schon gefuellt
        if gecacht is not None:
            return gecacht
        wert = await _sicher(quelle())
        if wert is None:
            return ersatz
        await cache.setze(schluessel, wert, ttl=ttl)
        return wert


async def _warn(o):
    return await _gecacht(f"weather:warn:{o.slug}", TTL_WARN, lambda: warnungen.hole(o.lat, o.lon), [])


async def _blitze(o):
    return await _gecacht(f"weather:blitze:{o.slug}", TTL_BLITZE, lambda: blitze.hole(o.lat, o.lon), None)


async def _luft(o):
    return await _gecacht(f"weather:luft:{o.slug}", TTL_LUFT, lambda: luftqualitaet.hole(o.lat, o.lon), None)


async def _pollen(o):
    return await _gecacht(f"weather:pollen:{o.slug}", TTL_POLLEN, lambda: pollen_dwd.hole(o.lat, o.lon), None)


@router.get("/complete/{ort}")
async def complete(ort: str) -> dict:
    """Alles zu einem Ort in einer Antwort (fuer den Erstaufbau). Setzt sich aus
    denselben gecachten Bereichen zusammen wie die Einzel-Endpunkte."""
    o = await _ort(ort)
    b = await _basis(o)
    luft, warn, blitz, pollen = await asyncio.gather(_luft(o), _warn(o), _blitze(o), _pollen(o))
    return wrap({**b, "luft": luft, "warnungen": warn, "blitze": blitz, "pollen": pollen})


# --- Einzel-Bereiche: jeder in seinem eigenen Frische-Takt abfragbar ---


@router.get("/basis/{ort}")
async def basis(ort: str) -> dict:
    """Aktuell, stuendlich, taeglich, Sonne - fuer den ~10-min-Takt."""
    return wrap(await _basis(await _ort(ort)))


@router.get("/warnungen/{ort}")
async def warnungen_ep(ort: str) -> dict:
    """Amtliche Warnungen - zeitkritisch."""
    return wrap(await _warn(await _ort(ort)))


@router.get("/blitze/{ort}")
async def blitze_ep(ort: str) -> dict:
    """Blitze im Umkreis - zeitkritisch."""
    return wrap(await _blitze(await _ort(ort)))


@router.get("/luft/{ort}")
async def luft_ep(ort: str) -> dict:
    """Luftqualitaet - traege."""
    return wrap(await _luft(await _ort(ort)))


@router.get("/pollen/{ort}")
async def pollen_ep(ort: str) -> dict:
    """Pollenflug - sehr traege."""
    return wrap(await _pollen(await _ort(ort)))


@router.get("/warnkarte")
async def warnkarte_ep() -> dict:
    """Amtliche Warn-Polygone (ganz Deutschland) als GeoJSON fuer das Karten-Overlay."""
    return wrap(await warnpolygone.hole())


@router.get("/klima/{ort}")
async def klima_ep(ort: str) -> dict:
    """Klima-Normale (Monatsmittel Temperatur + Niederschlag). Wird gespeichert und
    nur alle ~30 Tage neu aus dem Archiv berechnet."""
    o = await _ort(ort)
    async with SessionLocal() as session:
        row = await session.get(KlimaNormale, o.slug)
        if row is not None and (datetime.now() - row.stand) < timedelta(days=30):
            return wrap(json.loads(row.daten))
    try:
        daten = await klima.normalen(o.lat, o.lon)
    except Exception:
        if row is not None:
            return wrap(json.loads(row.daten))  # notfalls die gespeicherten (evtl. aelteren) Werte
        raise HTTPException(status_code=502, detail="Klima-Archiv nicht erreichbar")
    async with SessionLocal() as session:
        gespeichert = await session.get(KlimaNormale, o.slug)
        if gespeichert is not None:
            gespeichert.daten = json.dumps(daten)
            gespeichert.stand = datetime.now()
        else:
            session.add(KlimaNormale(ort=o.slug, daten=json.dumps(daten), stand=datetime.now()))
        await session.commit()
    return wrap(daten)


@router.get("/messjahre/{ort}")
async def messjahre_ep(ort: str) -> dict:
    """Verfuegbare Jahre und Variablen der aufgezeichneten Messwerte eines Ortes.

    Frischt die Aggregate dieses Ortes vorab auf, damit gerade erst aufgezeichnete
    Werte sofort erscheinen."""
    o = await _ort(ort)
    await klima_aggregat.aktualisiere([o.slug])
    jahre, variablen = await asyncio.gather(klima_aggregat.jahre(o.slug), klima_aggregat.variablen(o.slug))
    return wrap({"jahre": jahre, "variablen": variablen, "aktuelles_jahr": datetime.now().year})


@router.get("/jahresmesswerte/{ort}")
async def jahresmesswerte_ep(ort: str, jahr: int, variable: str = "temperatur") -> dict:
    """Echte, aggregierte Monatsmesswerte eines Ortes fuer ein Jahr und eine Variable.

    Liefert immer alle zwoelf Monate (fehlende als null), plus das aktuelle Jahr fuer
    die Markierung im Diagramm."""
    o = await _ort(ort)
    vorhanden = {m["monat"]: m for m in await klima_aggregat.monate(o.slug, variable, jahr)}
    monate = [
        {"monat": i, "kurz": MONATE_KURZ[i - 1], **({k: v for k, v in vorhanden[i].items() if k != "monat"} if i in vorhanden else {"mittel": None, "minimum": None, "maximum": None, "summe": None, "anzahl": 0})}
        for i in range(1, 13)
    ]
    return wrap({"jahr": jahr, "variable": variable, "aktuelles_jahr": datetime.now().year, "monate": monate})
