"""Aufzeichnungs-Manager: steuert, welche Orte mit welchen Variablen archiviert werden."""

from fastapi import APIRouter, Body
from sqlalchemy import func
from sqlmodel import select

from .. import ortsdienst
from ..db import SessionLocal
from ..models.aufzeichnung import AufzeichnungOrt
from ..models.messwert import Messwert
from ..schemas.envelope import wrap

router = APIRouter(prefix="/aufzeichnung", tags=["aufzeichnung"])

STANDARD_VARS = ["temperatur", "feuchte", "wind", "druck", "aqi", "pm2_5", "pm10", "o3", "no2"]
LABELS = {
    "temperatur": "Temperatur",
    "feuchte": "Feuchte",
    "wind": "Wind",
    "druck": "Druck",
    "aqi": "Luftgüte (AQI)",
    "pm2_5": "PM2,5",
    "pm10": "PM10",
    "o3": "Ozon",
    "no2": "NO₂",
}


@router.get("")
async def liste() -> dict:
    """Alle Orte mit ihrer Aufzeichnungs-Auswahl und der Zahl gespeicherter Werte."""
    async with SessionLocal() as session:
        rows = {r.ort: r for r in (await session.execute(select(AufzeichnungOrt))).scalars().all()}
        anzahl = dict((await session.execute(select(Messwert.ort, func.count()).group_by(Messwert.ort))).all())

    orte = await ortsdienst.alle()
    eintraege = []
    for o in orte:
        r = rows.get(o.slug)
        variablen = [v.strip() for v in r.variablen.split(",") if v.strip()] if r else list(STANDARD_VARS)
        eintraege.append(
            {
                "ort": o.slug,
                "name": o.name,
                "region": o.region,
                "variablen": variablen,
                "aktiv": r.aktiv if r else True,
                "anzahl": int(anzahl.get(o.slug, 0)),
            }
        )
    return wrap({"orte": eintraege, "verfuegbar": [{"wert": v, "label": LABELS[v]} for v in STANDARD_VARS]})


@router.put("/{ort}")
async def setze(ort: str, koerper: dict = Body(...)) -> dict:
    """Auswahl fuer einen Ort setzen (aktiv-Schalter und/oder Variablenliste)."""
    variablen = koerper.get("variablen")
    aktiv = koerper.get("aktiv")
    async with SessionLocal() as session:
        r = await session.get(AufzeichnungOrt, ort)
        if r is None:
            r = AufzeichnungOrt(ort=ort)
            session.add(r)
        if variablen is not None:
            r.variablen = ",".join(v for v in variablen if v in STANDARD_VARS)
        if aktiv is not None:
            r.aktiv = bool(aktiv)
        await session.commit()
        await session.refresh(r)
    return wrap({"ort": r.ort, "variablen": [v for v in r.variablen.split(",") if v], "aktiv": r.aktiv})
