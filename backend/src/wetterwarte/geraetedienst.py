"""Geräte, Gedächtnis und Protokoll in der Datenbank; Melden über einen Kanal (docs/WARNUNGEN.md).

Einzige Stelle, an der Router und Melder Geräte lesen und schreiben. `melde` verbindet Lage, Gedächtnis und
Einstellungen eines Geräts (melden.pruefe) und hält das Gedächtnis des Kanals nach."""

from collections.abc import Callable
from datetime import timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from . import melden
from .melden import Erinnerung
from .models.geraet import Geraet, Meldegedaechtnis, Meldung
from .models.ort import Ort
from .schemas.geraete import Ansage, GeraetAntwort, Meldeeinstellungen, Protokolleintrag, PushAbo
from .schemas.kompakt import Kompakt
from .schemas.lage import Quelle
from .zeit import jetzt

PROTOKOLL_TAGE = 30
PROTOKOLL_HOECHSTENS = 200  # je Gerät
PROTOKOLL_ANZEIGE = 20

# Aus welchem Datenbereich eine Quelle der Lage stammt (fehlt er, gilt sie als ausgefallen)
_BEREICH: dict[Quelle, str] = {"radar": "nowcast", "vorhersage": "basis", "amtlich": "warnungen", "blitze": "blitze"}


def einstellungen(g: Geraet) -> Meldeeinstellungen:
    return Meldeeinstellungen.model_validate(g.einstellungen or {})


async def antwort(session: AsyncSession, g: Geraet) -> GeraetAntwort:
    zeilen = await session.execute(
        select(Meldung).where(Meldung.geraet_id == g.id).order_by(Meldung.zeit.desc()).limit(PROTOKOLL_ANZEIGE)
    )
    return GeraetAntwort(
        id=g.id,
        einstellungen=einstellungen(g),
        push=g.push_endpunkt is not None,
        protokoll=[Protokolleintrag.model_validate(m, from_attributes=True) for m in zeilen.scalars()],
    )


async def anlegen(session: AsyncSession, ort: str | None) -> Geraet:
    g = Geraet(einstellungen=Meldeeinstellungen(orte=[ort] if ort else []).model_dump(mode="json"))
    session.add(g)
    await session.commit()
    return g


async def lies(session: AsyncSession, geraet_id: str) -> Geraet | None:
    g = await session.get(Geraet, geraet_id)
    if g is not None:
        g.gesehen = jetzt()
        await session.commit()
    return g


async def setze_einstellungen(session: AsyncSession, g: Geraet, e: Meldeeinstellungen) -> None:
    g.einstellungen = e.model_dump(mode="json")
    await session.commit()


async def setze_abo(session: AsyncSession, g: Geraet, abo: PushAbo) -> None:
    # Ein Browser-Abo gehört genau einem Gerät: nach einem Neuanlegen im selben Browser zieht es um.
    await session.execute(
        update(Geraet).where(Geraet.push_endpunkt == abo.endpoint, Geraet.id != g.id)
        .values(push_endpunkt=None, push_p256dh=None, push_auth=None)
    )
    g.push_endpunkt, g.push_p256dh, g.push_auth = abo.endpoint, abo.keys["p256dh"], abo.keys["auth"]
    await session.commit()


async def loesche_abo(session: AsyncSession, g: Geraet) -> None:
    g.push_endpunkt = g.push_p256dh = g.push_auth = None
    await session.execute(delete(Meldegedaechtnis).where(Meldegedaechtnis.geraet_id == g.id, Meldegedaechtnis.kanal == "push"))
    await session.commit()


async def protokolliere(session: AsyncSession, g: Geraet, kanal: str, ort: Ort, m: Ansage, zugestellt: bool) -> None:
    session.add(Meldung(geraet_id=g.id, kanal=kanal, ort=ort.slug, art=m.art, schluessel=m.schluessel, stufe=m.stufe,
                        titel=m.titel, text=m.text, zugestellt=zugestellt))
    await session.commit()


async def aufraeumen(session: AsyncSession) -> None:
    """Protokoll: höchstens 30 Tage und 200 Einträge je Gerät."""
    await session.execute(delete(Meldung).where(Meldung.zeit < jetzt() - timedelta(days=PROTOKOLL_TAGE)))
    rang = func.row_number().over(partition_by=Meldung.geraet_id, order_by=Meldung.zeit.desc()).label("rang")
    alt = select(Meldung.id, rang).subquery()
    await session.execute(delete(Meldung).where(Meldung.id.in_(select(alt.c.id).where(alt.c.rang > PROTOKOLL_HOECHSTENS))))
    await session.commit()


def ausgefallen(k: Kompakt) -> frozenset[Quelle]:
    return frozenset(q for q, bereich in _BEREICH.items() if k.bereiche.get(bereich) is None or k.bereiche[bereich].status == "fehlt")


async def melde(
    session: AsyncSession, g: Geraet, kanal: str, ort: Ort, k: Kompakt, zulassen: Callable[[Ansage], bool] = lambda _: True
) -> list[Ansage]:
    """Neue Meldungen eines Kanals für einen Ort; das Gedächtnis des Kanals wird nachgeführt."""
    zeile = await session.get(Meldegedaechtnis, (g.id, kanal, ort.slug))
    vorher = {s: Erinnerung.model_validate(e) for s, e in (zeile.eintraege if zeile else {}).items()}
    meldungen, neu = melden.pruefe(k.lage, vorher, einstellungen(g), jetzt(), zulassen, ausgefallen(k))
    eintraege = {s: e.model_dump(mode="json") for s, e in neu.items()}
    await session.execute(
        pg_insert(Meldegedaechtnis)
        .values(geraet_id=g.id, kanal=kanal, ort=ort.slug, eintraege=eintraege, aktualisiert=jetzt())
        .on_conflict_do_update(index_elements=["geraet_id", "kanal", "ort"], set_={"eintraege": eintraege, "aktualisiert": jetzt()})
    )
    await session.commit()
    return meldungen
