"""Geräte für aktive Warnungen: Einstellungen, Push-Abo, Probe, Ansagen abholen (docs/WARNUNGEN.md)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .. import geraetedienst, kompakt, ortsdienst, push
from ..ansagen import text
from ..config import settings
from ..db import get_session
from ..models.geraet import Geraet
from ..models.ort import Ort
from ..schemas.envelope import wrap
from ..schemas.geraete import GeraetAnlage, Meldeeinstellungen, PushAbo

router = APIRouter(tags=["geraete"])


async def _geraet(geraet_id: str, session: AsyncSession) -> Geraet:
    g = await geraetedienst.lies(session, geraet_id)
    if g is None:
        raise HTTPException(status_code=404, detail="Gerät unbekannt")
    return g


async def _ort(slug: str) -> Ort:
    o = await ortsdienst.per_slug(slug)
    if o is None:
        raise HTTPException(status_code=404, detail="Ort unbekannt")
    return o


@router.get("/push/schluessel")
async def schluessel() -> dict:
    """Öffentlicher VAPID-Schlüssel für das Push-Abo des Browsers und die sichere Adresse der App (falls bekannt)."""
    return wrap({"schluessel": await push.oeffentlich(), "sichere_adresse": settings.sichere_adresse})


@router.post("/geraete", status_code=201)
async def anlegen(eingabe: GeraetAnlage, session: AsyncSession = Depends(get_session)) -> dict:
    """Gerät anlegen; der Startort ist für Mitteilungen vorgewählt."""
    if eingabe.ort:
        await _ort(eingabe.ort)
    g = await geraetedienst.anlegen(session, eingabe.ort)
    return wrap((await geraetedienst.antwort(session, g)).model_dump(mode="json"))


@router.get("/geraete/{geraet_id}")
async def lesen(geraet_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    g = await _geraet(geraet_id, session)
    return wrap((await geraetedienst.antwort(session, g)).model_dump(mode="json"))


@router.put("/geraete/{geraet_id}/einstellungen")
async def einstellen(geraet_id: str, eingabe: Meldeeinstellungen, session: AsyncSession = Depends(get_session)) -> dict:
    g = await _geraet(geraet_id, session)
    for slug in eingabe.orte:
        await _ort(slug)
    await geraetedienst.setze_einstellungen(session, g, eingabe)
    return wrap((await geraetedienst.antwort(session, g)).model_dump(mode="json"))


@router.put("/geraete/{geraet_id}/push")
async def abonnieren(geraet_id: str, abo: PushAbo, session: AsyncSession = Depends(get_session)) -> dict:
    g = await _geraet(geraet_id, session)
    await geraetedienst.setze_abo(session, g, abo)
    return wrap((await geraetedienst.antwort(session, g)).model_dump(mode="json"))


@router.delete("/geraete/{geraet_id}/push")
async def abbestellen(geraet_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    g = await _geraet(geraet_id, session)
    await geraetedienst.loesche_abo(session, g)
    return wrap((await geraetedienst.antwort(session, g)).model_dump(mode="json"))


@router.post("/geraete/{geraet_id}/probe")
async def probe(geraet_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    """Probemitteilung senden: "ok", "weg" (Abo erloschen, entfernt), "fehler" oder "kein_abo"."""
    g = await _geraet(geraet_id, session)
    if g.push_endpunkt is None or g.push_p256dh is None or g.push_auth is None:
        return wrap({"ergebnis": "kein_abo"})
    nutzlast = {"titel": "Wetterwarte: Probemitteilung", "text": text(["probe"]), "tag": "probe", "url": "/telefon?ansicht=mehr", "stufe": 1}
    ergebnis = await push.sende(g.push_endpunkt, g.push_p256dh, g.push_auth, nutzlast, ttl=600, dringend=False)
    if ergebnis == "weg":
        await geraetedienst.loesche_abo(session, g)
    return wrap({"ergebnis": ergebnis})


@router.post("/geraete/{geraet_id}/ansagen")
async def ansagen_abholen(geraet_id: str, ort: str = Query(...), session: AsyncSession = Depends(get_session)) -> dict:
    """Neue Ansagen für den gezeigten Ort; die App spricht sie (Gedächtnis des Kanals ansage, ohne Nachtruhe)."""
    g = await _geraet(geraet_id, session)
    o = await _ort(ort)
    meldungen = await geraetedienst.melde(session, g, "ansage", o, await kompakt.lade(o))
    for m in meldungen:
        await geraetedienst.protokolliere(session, g, "ansage", o, m, True)
    return wrap([m.model_dump(mode="json") for m in meldungen])


@router.delete("/geraete/{geraet_id}", status_code=204)
async def vergessen(geraet_id: str, session: AsyncSession = Depends(get_session)) -> Response:
    g = await session.get(Geraet, geraet_id)
    if g is not None:
        await session.delete(g)
        await session.commit()
    return Response(status_code=204)
