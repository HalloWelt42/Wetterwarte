"""Datenbereiche mit Stand und Status.

Jeder Bereich (Vorhersage, Warnungen, Blitze, Luft, Pollen) liegt mit dem Zeitpunkt seines
Abrufs im Redis-Zwischenspeicher. Ist er frisch, kommt er ohne Abruf; sonst wird die Quelle
gefragt. Scheitert sie, kommt der letzte gute Stand als "alt", solange er nicht zu alt ist,
danach "fehlt". So sieht die Oberfläche immer, wie verlässlich ein Wert ist, und ein Ausfall
der Warnquelle sieht nie wie "keine Warnungen" aus.

Ein Lock je Schlüssel verhindert parallele Abrufe derselben Quelle, eine kurze Sperre nach
einem Fehlschlag verhindert, dass jede Anfrage eine tote Quelle erneut anfragt."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Literal, TypeVar

from . import cache
from .zeit import jetzt

log = logging.getLogger(__name__)

T = TypeVar("T")
Status = Literal["ok", "alt", "fehlt"]

# Nach einem Fehlschlag so lange nicht erneut fragen (Sekunden).
SPERRE_NACH_FEHLER = 30


@dataclass(frozen=True)
class Regel:
    """Frische und Haltbarkeit eines Bereichs in Sekunden."""

    frisch: int  # so lange gilt ein Stand ohne neuen Abruf
    haltbar: int  # so lange darf ein alter Stand bei Ausfall noch gezeigt werden


@dataclass
class Ergebnis(Generic[T]):
    wert: T | None
    status: Status
    stand: datetime | None

    def meta(self) -> dict:
        return {"status": self.status, "stand": self.stand.isoformat() if self.stand else None}


_locks: dict[str, asyncio.Lock] = {}
_fehlschlag: dict[str, float] = {}


def _lock(schluessel: str) -> asyncio.Lock:
    sperre = _locks.get(schluessel)
    if sperre is None:
        sperre = _locks[schluessel] = asyncio.Lock()
    return sperre


def _eintrag(roh: dict | None) -> tuple[object, datetime] | None:
    if not roh or "stand" not in roh:
        return None
    try:
        return roh.get("wert"), datetime.fromisoformat(roh["stand"])
    except (TypeError, ValueError):
        return None


async def lade(schluessel: str, regel: Regel, quelle: Callable[[], Awaitable[T]]) -> Ergebnis[T]:
    """Bereich holen: frisch aus dem Speicher, sonst von der Quelle, sonst alt oder fehlt."""
    vorhanden = _eintrag(await cache.hole(schluessel))
    if vorhanden and (jetzt() - vorhanden[1]).total_seconds() < regel.frisch:
        return Ergebnis(vorhanden[0], "ok", vorhanden[1])  # type: ignore[arg-type]

    async with _lock(schluessel):
        vorhanden = _eintrag(await cache.hole(schluessel))
        if vorhanden and (jetzt() - vorhanden[1]).total_seconds() < regel.frisch:
            return Ergebnis(vorhanden[0], "ok", vorhanden[1])  # type: ignore[arg-type]

        if time.monotonic() - _fehlschlag.get(schluessel, -1e9) >= SPERRE_NACH_FEHLER:
            try:
                wert = await quelle()
            except Exception as fehler:  # jede Quelle kann auf eigene Art scheitern
                _fehlschlag[schluessel] = time.monotonic()
                log.warning("Quelle für %s nicht verfügbar: %s", schluessel, fehler)
            else:
                _fehlschlag.pop(schluessel, None)
                stand = jetzt()
                await cache.setze(schluessel, {"wert": wert, "stand": stand.isoformat()}, ttl=regel.haltbar)
                return Ergebnis(wert, "ok", stand)

    if vorhanden and (jetzt() - vorhanden[1]).total_seconds() < regel.haltbar:
        return Ergebnis(vorhanden[0], "alt", vorhanden[1])  # type: ignore[arg-type]
    return Ergebnis(None, "fehlt", vorhanden[1] if vorhanden else None)
