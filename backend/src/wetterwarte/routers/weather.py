"""Wetter-Endpunkte - echte Daten ueber gekapselte Provider.

Die Datenherkunft ist gekapselt; ein Wechsel auf den lokal gespiegelten Dienst
oder einen eigenen DWD-Ingester aendert nur den Provider, nicht die Form.

Datenfrische pro Bereich: zeitkritische Daten (Warnungen, Blitze) werden kurz
gecacht, traege Daten (Vorhersage, Luft, Pollen) laenger. Das Frontend fragt
jeden Bereich in seinem eigenen Takt ab (siehe wetter.svelte.ts).
"""

import asyncio
import json
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response

from .. import kompakt, klima_aggregat, ortsdienst, wetterdienst
from ..db import SessionLocal
from ..models.klima import KlimaNormale
from ..providers import karten_gitter, klima, openmeteo, warnpolygone, warnungen
from ..schemas.envelope import wrap
from ..zeit import jetzt, zone

router = APIRouter(prefix="/wetter", tags=["wetter"])

# Kurze Monatsnamen fuer die Diagramm-Beschriftung.
MONATE_KURZ = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


async def _ort(ort: str):
    o = await ortsdienst.per_slug(ort.lower())
    if o is None:
        raise HTTPException(status_code=404, detail="Ort nicht bekannt")
    return o


async def _darstellung_basis(o, roh: dict | None) -> dict | None:
    """Desktop-Form der Vorhersage; den Kurzfrist-Regen rechnet kompakt.regen_kurzfrist (Radar vor Modell)."""
    if not roh:
        return None
    nowcast = await wetterdienst.nowcast(o)
    return {**openmeteo.darstellung(roh, o.name, o.region, o.lat, o.lon), "nowcast": kompakt.regen_kachel(kompakt.regen_kurzfrist(roh, nowcast.wert))}


def _darstellung_warn(o, roh: list | None) -> list | None:
    return warnungen.darstellung(roh, o.zeitzone) if roh is not None else None


@router.get("/complete/{ort}")
async def complete(ort: str) -> dict:
    """Alles zu einem Ort in einer Antwort (Desktop-Form). Status je Bereich in meta.bereiche."""
    o = await _ort(ort)
    b, luft, warn, blitz, pollen = await asyncio.gather(
        wetterdienst.basis(o), wetterdienst.luft(o), wetterdienst.warnungen(o), wetterdienst.blitze(o), wetterdienst.pollen(o)
    )
    if b.wert is None:
        raise HTTPException(status_code=502, detail="Wetterquelle nicht erreichbar")
    antwort = wrap({
        **(await _darstellung_basis(o, b.wert) or {}),
        "luft": luft.wert,
        "warnungen": _darstellung_warn(o, warn.wert),
        "blitze": blitz.wert,
        "pollen": pollen.wert,
    })
    antwort["meta"]["bereiche"] = {
        name: e.meta() for name, e in (("basis", b), ("luft", luft), ("warnungen", warn), ("blitze", blitz), ("pollen", pollen))
    }
    return antwort


@router.get("/kompakt/{ort}")
async def kompakt_ep(ort: str) -> dict:
    """Alles für die Telefonansicht in einem Abruf: Rohwerte, Zeiten mit Versatz, Status je
    Bereich (siehe schemas/kompakt.py und docs/TELEFON.md)."""
    o = await _ort(ort)
    return wrap((await kompakt.lade(o)).model_dump(mode="json"))


# --- Einzel-Bereiche: jeder in seinem eigenen Frische-Takt abfragbar. Fehlt ein Bereich,
# kommt data = null mit meta.status = "fehlt" (kein Fehlercode), damit die Oberfläche den
# Zustand zeigen kann.


@router.get("/basis/{ort}")
async def basis(ort: str) -> dict:
    """Aktuell, stuendlich, taeglich, Sonne."""
    o = await _ort(ort)
    e = await wetterdienst.basis(o)
    return wrap(await _darstellung_basis(o, e.wert), ergebnis=e)


@router.get("/warnungen/{ort}")
async def warnungen_ep(ort: str) -> dict:
    """Amtliche Warnungen - zeitkritisch. Bei Ausfall data = null, nie eine leere Liste."""
    o = await _ort(ort)
    e = await wetterdienst.warnungen(o)
    return wrap(_darstellung_warn(o, e.wert), ergebnis=e)


@router.get("/blitze/{ort}")
async def blitze_ep(ort: str) -> dict:
    """Blitze im Umkreis - zeitkritisch."""
    e = await wetterdienst.blitze(await _ort(ort))
    return wrap(e.wert, ergebnis=e)


@router.get("/luft/{ort}")
async def luft_ep(ort: str) -> dict:
    """Luftqualitaet - traege."""
    e = await wetterdienst.luft(await _ort(ort))
    return wrap(e.wert, ergebnis=e)


@router.get("/pollen/{ort}")
async def pollen_ep(ort: str) -> dict:
    """Pollenflug - sehr traege."""
    e = await wetterdienst.pollen(await _ort(ort))
    return wrap(e.wert, ergebnis=e)


@router.get("/warnkarte")
async def warnkarte_ep() -> dict:
    """Amtliche Warn-Polygone (ganz Deutschland) als GeoJSON fuer das Karten-Overlay."""
    return wrap(await warnpolygone.hole())


@router.get("/kartendaten")
async def kartendaten_ep() -> dict:
    """Overlay-Daten (Temperatur-Bild-Ecken + Wind-Gitter) in einem Abruf."""
    try:
        return wrap(await karten_gitter.kartendaten())
    except Exception as fehler:
        raise HTTPException(status_code=502, detail=f"Gitterdaten nicht erreichbar: {fehler}") from fehler


@router.get("/temperatur.png")
async def temperatur_png_ep() -> Response:
    """Temperatur als glattes Farbfeld (halbtransparentes PNG) fuer das Karten-Overlay."""
    try:
        png = await karten_gitter.temperatur_png()
    except Exception as fehler:
        raise HTTPException(status_code=502, detail=f"Temperaturfeld nicht erreichbar: {fehler}") from fehler
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "public, max-age=300"})


@router.get("/klima/{ort}")
async def klima_ep(ort: str) -> dict:
    """Klima-Normale (Monatsmittel Temperatur + Niederschlag). Wird gespeichert und
    nur alle ~30 Tage neu aus dem Archiv berechnet."""
    o = await _ort(ort)
    async with SessionLocal() as session:
        row = await session.get(KlimaNormale, o.slug)
        if row is not None and (jetzt() - row.stand) < timedelta(days=30):
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
            gespeichert.stand = jetzt()
        else:
            session.add(KlimaNormale(ort=o.slug, daten=json.dumps(daten), stand=jetzt()))
        await session.commit()
    return wrap(daten)


@router.get("/messjahre/{ort}")
async def messjahre_ep(ort: str) -> dict:
    """Verfuegbare Jahre und Variablen der aufgezeichneten Messwerte eines Ortes.

    Frischt die Aggregate dieses Ortes vorab auf, damit gerade erst aufgezeichnete
    Werte sofort erscheinen."""
    o = await _ort(ort)
    heute = jetzt().astimezone(zone(o.zeitzone))
    # Nur den laufenden Monat: ältere verdichtet der Recorder, sie ändern sich nicht mehr.
    await klima_aggregat.aktualisiere([o.slug], monat=(heute.year, heute.month))
    jahre, variablen = await asyncio.gather(klima_aggregat.jahre(o.slug), klima_aggregat.variablen(o.slug))
    return wrap({"jahre": jahre, "variablen": variablen, "aktuelles_jahr": jetzt().astimezone(zone(o.zeitzone)).year})


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
    return wrap({"jahr": jahr, "variable": variable, "aktuelles_jahr": jetzt().astimezone(zone(o.zeitzone)).year, "monate": monate})
