"""Endpunkte fuer die Ortsliste: per Suche finden, hinzufuegen, entfernen.

Die Liste ist datengetrieben (Datenbank); es gibt keine fest verdrahteten Orte
mehr im Quellcode - der Nutzer waehlt seine Orte selbst per Suche.
"""

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .. import ortsdienst
from ..db import get_session
from ..models.ort import Ort
from ..providers import geocoding
from ..schemas.envelope import wrap

router = APIRouter(prefix="/orte", tags=["orte"])


class OrtEingabe(BaseModel):
    name: str
    region: str = ""
    land: str = ""
    lat: float
    lon: float
    zeitzone: str = ""


@router.get("")
async def liste() -> dict:
    return wrap([o.model_dump() for o in await ortsdienst.alle()])


@router.get("/suche")
async def orte_suchen(q: str = "") -> dict:
    """Geocoding-Treffer zu einem Suchbegriff (Name, Region, Land, Koordinaten)."""
    try:
        treffer = await geocoding.suche(q)
    except Exception:
        treffer = []
    return wrap(treffer)


@router.post("")
async def anlegen(eingabe: OrtEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    ort = await ortsdienst.anlegen(session, eingabe.name, eingabe.region, eingabe.land, eingabe.lat, eingabe.lon, eingabe.zeitzone)
    return wrap(ort.model_dump())


@router.put("/reihenfolge")
async def reihenfolge(ids: list[str] = Body(..., embed=True), session: AsyncSession = Depends(get_session)) -> dict:
    """Neue Reihenfolge der Orte speichern (Liste der Orte-IDs in Zielreihenfolge)."""
    for i, oid in enumerate(ids):
        ort = await session.get(Ort, oid)
        if ort is not None:
            ort.reihenfolge = i
    await session.commit()
    return wrap({"ok": True})


@router.delete("/{ort_id}")
async def loeschen(ort_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    ort = await session.get(Ort, ort_id)
    if ort is not None:
        await session.delete(ort)
        await session.commit()
    return wrap({"geloescht": True})
