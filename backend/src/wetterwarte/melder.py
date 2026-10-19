"""Melder: prüft im Hintergrund die Lage aller abonnierten Orte und sendet Mitteilungen (docs/WARNUNGEN.md).

Läuft wie die Aufzeichnung als Aufgabe im Backend-Prozess. Je Takt wird jeder Ort einmal geladen (über die
Zwischenspeicher der Bereiche, also ohne zusätzliche Abrufe, wenn die Daten frisch sind), dann bekommt jedes
Gerät, was für seine Orte neu ist. Die Nachtruhe gilt in der Ortszeit des gemeldeten Orts."""

import asyncio
import logging
import time

from sqlalchemy import select

from . import geraetedienst, kompakt, ortsdienst, push
from .config import settings
from .db import SessionLocal
from .melden import in_ruhe
from .models.geraet import Geraet
from .models.ort import Ort
from .schemas.geraete import Ansage, Meldeeinstellungen
from .schemas.kompakt import Kompakt
from .zeit import jetzt, zone

log = logging.getLogger(__name__)

ERSTER_LAUF_S = 60  # nach dem Start erst die Bereiche warm werden lassen
# Wie lange der Push-Dienst eine Mitteilung höchstens zustellen soll (danach ist sie überholt)
TTL_S = {"niederschlag": 20 * 60, "gewitter": 20 * 60, "wind": 2 * 3600, "warnung": 6 * 3600}
ENTWARNUNG_TTL_S = 30 * 60


def blatt(m: Ansage) -> str:
    """Welches Blatt die Telefonansicht beim Antippen öffnet."""
    return "warnungen" if m.art == "warnung" and not m.entwarnung else "lage"


def nutzlast(ort: Ort, m: Ansage) -> dict:
    return {
        "titel": f"{ort.name}: {m.titel}",
        "text": m.text,
        "tag": f"{ort.slug}:{m.schluessel}",
        "url": f"/telefon?ort={ort.slug}&blatt={blatt(m)}",
        "stufe": m.stufe,
    }


def nachtruhe(einst: Meldeeinstellungen, ort: Ort):
    stunde = jetzt().astimezone(zone(ort.zeitzone)).hour
    ruhig = in_ruhe(einst, stunde)
    return lambda m: not ruhig or m.stufe >= einst.nachtruhe.ab_stufe


async def _sende(g: Geraet, ort: Ort, m: Ansage) -> str:
    assert g.push_endpunkt and g.push_p256dh and g.push_auth
    ttl = ENTWARNUNG_TTL_S if m.entwarnung else TTL_S.get(m.art, 3600)
    return await push.sende(g.push_endpunkt, g.push_p256dh, g.push_auth, nutzlast(ort, m), ttl, dringend=m.stufe >= 3)


async def _geraet(geraet_id: str, lagen: dict[str, tuple[Ort, Kompakt]]) -> None:
    async with SessionLocal() as session:
        g = await session.get(Geraet, geraet_id)
        if g is None or g.push_endpunkt is None:
            return
        einst = geraetedienst.einstellungen(g)
        for slug in einst.orte:
            if slug not in lagen:
                continue
            ort, k = lagen[slug]
            for m in await geraetedienst.melde(session, g, "push", ort, k, nachtruhe(einst, ort)):
                versand = await _sende(g, ort, m)
                await geraetedienst.protokolliere(session, g, "push", ort, m, versand == "ok")
                if versand == "weg":
                    log.info("Push-Abo von Gerät %s gibt es nicht mehr, entfernt", g.id)
                    await geraetedienst.loesche_abo(session, g)
                    return


async def runde() -> None:
    async with SessionLocal() as session:
        geraete = (await session.execute(select(Geraet).where(Geraet.push_endpunkt.is_not(None)))).scalars().all()
        slugs = {slug for g in geraete for slug in geraetedienst.einstellungen(g).orte}
    lagen: dict[str, tuple[Ort, Kompakt]] = {}
    for slug in sorted(slugs):
        ort = await ortsdienst.per_slug(slug)
        if ort is not None:
            lagen[slug] = (ort, await kompakt.lade(ort))
    for g in geraete:
        try:
            await _geraet(g.id, lagen)
        except Exception:
            log.exception("Melden an Gerät %s gescheitert", g.id)
    async with SessionLocal() as session:
        await geraetedienst.aufraeumen(session)


async def schleife() -> None:
    if settings.melder_takt_s <= 0:
        log.info("Melder abgeschaltet (MELDER_TAKT_S=0)")
        return
    await asyncio.sleep(ERSTER_LAUF_S)
    while True:
        beginn = time.monotonic()
        try:
            await runde()
        except Exception:
            log.exception("Melder-Runde gescheitert")
        await asyncio.sleep(max(10.0, settings.melder_takt_s - (time.monotonic() - beginn)))
