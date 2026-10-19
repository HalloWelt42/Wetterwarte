"""Wetterdaten je Ort und Bereich, mit Stand und Status (siehe bereiche.py).

Einzige Stelle, an der Router, Aufzeichnung und Telefon-Endpunkt an die Quellen kommen. Jeder
Bereich hat seine eigene Frische, weil sich Blitze im Minutentakt ändern, Pollen einmal am Tag."""

from . import bereiche, ortsdienst
from .bereiche import Ergebnis, Regel
from .models.ort import Ort
from .providers import blitze as blitze_quelle
from .providers import luftqualitaet, nowcast as nowcast_quelle, openmeteo, pollen_dwd, radar
from .providers import warnungen as warn_quelle

STUNDE = 3600

REGELN: dict[str, Regel] = {
    "basis": Regel(frisch=300, haltbar=6 * STUNDE),  # Vorhersage und aktuelle Werte
    "warnungen": Regel(frisch=120, haltbar=30 * 60),  # alte Warnungen nur kurz zeigen
    "blitze": Regel(frisch=60, haltbar=10 * 60),
    "luft": Regel(frisch=900, haltbar=6 * STUNDE),
    "pollen": Regel(frisch=STUNDE, haltbar=48 * STUNDE),
    "nowcast": Regel(frisch=240, haltbar=20 * 60),  # der Wetterdienst rechnet alle 5 Minuten neu
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


async def _nowcast_aller_orte() -> dict:
    orte = await ortsdienst.alle()
    return await nowcast_quelle.hole({o.slug: radar.punkt_index(o.lat, o.lon) for o in orte})


async def nowcast(o: Ort) -> Ergebnis[dict]:
    """Radar-Nowcast am Ort: {basis, versatz_min, werte}. Wert None bei Status ok heißt: der Ort liegt außerhalb
    des Radargebiets. Ein eben angelegter Ort, den der letzte Abruf noch nicht kannte, fehlt bis zum nächsten."""
    alle = await bereiche.lade("bereich:nowcast", REGELN["nowcast"], _nowcast_aller_orte)
    if alle.wert is None:
        return Ergebnis(None, alle.status, alle.stand)
    werte = alle.wert["reihen"].get(o.slug)
    if werte is not None:
        return Ergebnis({"basis": alle.wert["basis"], "versatz_min": alle.wert["versatz_min"], "werte": werte}, alle.status, alle.stand)
    if o.slug in alle.wert["ausserhalb"]:
        return Ergebnis(None, alle.status, alle.stand)
    return Ergebnis(None, "fehlt", alle.stand)
