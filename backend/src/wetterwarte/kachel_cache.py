"""Offline-Kachel-Cache auf der Platte (themengetrennt je Karten-Anbieter) plus
Fuell-Bot, der Kacheln fuer Deutschland vorlaedt (mehr rund um den Wohnort,
Satellit progressiv) - mit Fortschritt, Fehler- und Fertig-Logik.

Die Kacheln kommen vom lokalen lightningmap-Dienst; hier werden sie dauerhaft
zwischengespeichert, damit die Karte auch bei Internet-/Dienst-Ausfall laedt und
schneller wird. Der Cache ist die einzige Wahrheit fuer Speicher-Statistik + Bot.
"""

import asyncio
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import ortsdienst
from .config import settings

# Bekannte Karten-Anbieter (Themen). Basiskarten + Beschriftung + Satellit.
ANBIETER = ["dark", "light", "satellite", "voyager"]
# Deutschland-Bbox (lon/lat).
DE = (5.8, 47.2, 15.1, 55.1)

_erlaubt = re.compile(r"^[a-z0-9-]{1,32}$")


def _cache_dir() -> Path:
    p = Path(settings.kachel_cache_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _pfad(anbieter: str, z: int, x: int, y: int) -> Path:
    return _cache_dir() / anbieter / str(z) / str(x) / f"{y}.png"


def medientyp(daten: bytes) -> str:
    """Bildtyp anhand der Magic-Bytes (Kacheln sind je nach Anbieter JPEG oder PNG)."""
    if daten[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if daten[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if daten[:4] in (b"RIFF",) and daten[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


async def hole(anbieter: str, z: int, x: int, y: int) -> bytes | None:
    """Kachel aus dem Cache lesen; bei Fehltreffer vom Kachel-Dienst holen + ablegen."""
    if not _erlaubt.match(anbieter):
        return None
    pfad = _pfad(anbieter, z, x, y)
    if pfad.exists():
        try:
            return pfad.read_bytes()
        except OSError:
            pass
    url = f"{settings.lightning_base}/api/tile/{anbieter}/{z}/{x}/{y}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            antwort = await client.get(url)
            antwort.raise_for_status()
            daten = antwort.content
    except Exception:
        return None
    try:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        tmp = pfad.with_suffix(".tmp")
        tmp.write_bytes(daten)
        tmp.replace(pfad)  # atomar, keine halben Dateien
    except OSError:
        pass
    return daten


def statistik() -> dict:
    """Belegung je Anbieter (Anzahl Kacheln + Bytes) und gesamt."""
    themen = []
    gesamt_anzahl = gesamt_bytes = 0
    for anbieter in ANBIETER:
        wurzel = _cache_dir() / anbieter
        anzahl = byte = 0
        if wurzel.exists():
            for verzeichnis, _unter, dateien in os.walk(wurzel):
                for d in dateien:
                    if d.endswith(".png"):
                        anzahl += 1
                        try:
                            byte += os.path.getsize(os.path.join(verzeichnis, d))
                        except OSError:
                            pass
        themen.append({"anbieter": anbieter, "anzahl": anzahl, "bytes": byte})
        gesamt_anzahl += anzahl
        gesamt_bytes += byte
    return {"themen": themen, "anzahl": gesamt_anzahl, "bytes": gesamt_bytes}


# --- Fuell-Bot -----------------------------------------------------------------

_zustand: dict = {
    "laufend": False,
    "gesamt": 0,
    "fertig": 0,
    "fehler": 0,
    "anbieter": "",
    "gebiet": "",
    "abbrechen": False,
    "fehlermeldung": "",
    "stand": None,
}
_task: asyncio.Task | None = None


def zustand() -> dict:
    return {k: v for k, v in _zustand.items() if k != "abbrechen"}


def _kacheln_im_gebiet(bbox: tuple[float, float, float, float], z: int) -> list[tuple[int, int, int]]:
    lon0, lat0, lon1, lat1 = bbox
    n = 2**z
    x0 = int((lon0 + 180) / 360 * n)
    x1 = int((lon1 + 180) / 360 * n)

    def _y(lat: float) -> int:
        return int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)

    y_nord, y_sued = _y(lat1), _y(lat0)
    return [(z, x, y) for x in range(x0, x1 + 1) for y in range(y_nord, y_sued + 1)]


async def _lauf(anbieter_liste: list[str], z_de: int, z_heimat: int, heim: tuple[float, float]) -> None:
    lon, lat = heim
    heimat_bbox = (lon - 1.1, lat - 0.8, lon + 1.1, lat + 0.8)
    aufgaben: list[tuple[str, str, int, int, int]] = []
    for anbieter in anbieter_liste:
        for z in range(5, z_de + 1):
            for (_z, x, y) in _kacheln_im_gebiet(DE, z):
                aufgaben.append((anbieter, "deutschland", z, x, y))
        for z in range(z_de + 1, z_heimat + 1):
            for (_z, x, y) in _kacheln_im_gebiet(heimat_bbox, z):
                aufgaben.append((anbieter, "heimat", z, x, y))
    _zustand.update(gesamt=len(aufgaben), fertig=0, fehler=0, laufend=True, abbrechen=False, fehlermeldung="")
    sem = asyncio.Semaphore(6)

    async def _eine(a: str, gebiet: str, z: int, x: int, y: int) -> None:
        async with sem:
            if _zustand["abbrechen"]:
                return
            _zustand["anbieter"], _zustand["gebiet"] = a, gebiet
            res = await hole(a, z, x, y)
            if res is None:
                _zustand["fehler"] += 1
            else:
                _zustand["fertig"] += 1

    try:
        # In Bloecken abarbeiten, damit Abbruch schnell greift.
        for i in range(0, len(aufgaben), 60):
            if _zustand["abbrechen"]:
                break
            await asyncio.gather(*[_eine(*a) for a in aufgaben[i : i + 60]])
    except Exception as fehler:  # pragma: no cover - Schutz
        _zustand["fehlermeldung"] = str(fehler)
    finally:
        _zustand["laufend"] = False
        _zustand["stand"] = datetime.now(timezone.utc).isoformat()


async def starte(anbieter_liste: list[str], z_de: int = 8, z_heimat: int = 11) -> dict:
    """Fuell-Bot starten (falls nicht schon laufend)."""
    global _task
    if _zustand["laufend"]:
        return zustand()
    anbieter_liste = [a for a in anbieter_liste if a in ANBIETER] or ANBIETER
    z_de = max(5, min(10, z_de))
    z_heimat = max(z_de, min(13, z_heimat))
    start = await ortsdienst.per_slug((await _startort_slug()) or "")
    heim = (start.lon, start.lat) if start else (10.45, 51.16)
    _zustand.update(laufend=True, abbrechen=False, fertig=0, fehler=0, gesamt=0, fehlermeldung="")
    _task = asyncio.create_task(_lauf(anbieter_liste, z_de, z_heimat, heim))
    return zustand()


async def _startort_slug() -> str | None:
    orte = await ortsdienst.alle()
    fav = next((o for o in orte if getattr(o, "ist_start", False)), None)
    return (fav or (orte[0] if orte else None)).slug if orte else None


def stoppe() -> dict:
    if _zustand["laufend"]:
        _zustand["abbrechen"] = True
    return zustand()
