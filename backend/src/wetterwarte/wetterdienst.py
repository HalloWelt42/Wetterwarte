"""Wetterdaten je Ort und Bereich, mit Stand und Status (siehe bereiche.py).

Einzige Stelle, an der Router, Aufzeichnung und Telefon-Endpunkt an die Quellen kommen. Jeder
Bereich hat seine eigene Frische, weil sich Blitze im Minutentakt ändern, Pollen einmal am Tag."""

from . import bereiche
from .bereiche import Ergebnis, Regel
from .models.ort import Ort
from .providers import blitze as blitze_quelle
from .providers import luftqualitaet, openmeteo, pollen_dwd
from .providers import warnungen as warn_quelle

STUNDE = 3600

REGELN: dict[str, Regel] = {
    "basis": Regel(frisch=300, haltbar=6 * STUNDE),  # Vorhersage und aktuelle Werte
    "warnungen": Regel(frisch=120, haltbar=30 * 60),  # alte Warnungen nur kurz zeigen
    "blitze": Regel(frisch=60, haltbar=10 * 60),
    "luft": Regel(frisch=900, haltbar=6 * STUNDE),
    "pollen": Regel(frisch=STUNDE, haltbar=48 * STUNDE),
}


async def basis(o: Ort) -> Ergebnis[dict]:
    """Rohantwort von Open-Meteo (aktuell, Stunden, Tage, 15 Minuten)."""
    return await bereiche.lade(f"bereich:basis:{o.slug}", REGELN["basis"], lambda: openmeteo.hole(o.lat, o.lon))


async def warnungen(o: Ort) -> Ergebnis[list]:
    return await bereiche.lade(
        f"bereich:warnungen:{o.slug}", REGELN["warnungen"], lambda: warn_quelle.hole(o.lat, o.lon, o.zeitzone)
    )


async def blitze(o: Ort) -> Ergebnis[dict]:
    return await bereiche.lade(f"bereich:blitze:{o.slug}", REGELN["blitze"], lambda: blitze_quelle.hole(o.lat, o.lon))


async def luft(o: Ort) -> Ergebnis[dict]:
    return await bereiche.lade(f"bereich:luft:{o.slug}", REGELN["luft"], lambda: luftqualitaet.hole(o.lat, o.lon))


async def pollen(o: Ort) -> Ergebnis[dict]:
    """Pollen nur in Deutschland; außerhalb ist der Wert None bei Status ok."""
    return await bereiche.lade(f"bereich:pollen:{o.slug}", REGELN["pollen"], lambda: pollen_dwd.hole(o.lat, o.lon))
