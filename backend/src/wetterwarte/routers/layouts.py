"""Endpunkte fuer benannte Dashboard-Layouts."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .. import telefon as telefon_katalog
from ..db import get_session
from ..models.layout import Layout
from ..schemas.envelope import wrap

router = APIRouter(prefix="/layouts", tags=["layouts"])


class LayoutEingabe(BaseModel):
    name: str | None = None
    daten: list | None = None
    ist_standard: bool | None = None
    icon: str | None = None
    telefon: telefon_katalog.TelefonLayout | None = None


def _gepruefte(t: telefon_katalog.TelefonLayout) -> dict:
    try:
        telefon_katalog.pruefe(t)
    except ValueError as fehler:
        raise HTTPException(status_code=422, detail=str(fehler)) from fehler
    return t.model_dump()


@router.get("")
async def liste(session: AsyncSession = Depends(get_session)) -> dict:
    ergebnis = await session.execute(select(Layout).order_by(Layout.ist_standard.desc(), Layout.name))
    return wrap([l.model_dump() for l in ergebnis.scalars().all()])


@router.post("")
async def anlegen(eingabe: LayoutEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    name = eingabe.name or "Neues Layout"
    t = _gepruefte(eingabe.telefon) if eingabe.telefon is not None else telefon_katalog.vorlage(name).model_dump()
    layout = Layout(name=name, daten=eingabe.daten or [], icon=eingabe.icon or "", telefon=t)
    session.add(layout)
    await session.commit()
    await session.refresh(layout)
    return wrap(layout.model_dump())


@router.put("/{layout_id}")
async def speichern(layout_id: str, eingabe: LayoutEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    layout = await session.get(Layout, layout_id)
    if layout is None:
        raise HTTPException(status_code=404, detail="Layout nicht gefunden")
    if eingabe.name is not None:
        layout.name = eingabe.name
    if eingabe.daten is not None:
        layout.daten = eingabe.daten
    if eingabe.icon is not None:
        layout.icon = eingabe.icon
    if eingabe.telefon is not None:
        layout.telefon = _gepruefte(eingabe.telefon)
    if eingabe.ist_standard is not None:
        if eingabe.ist_standard:
            # Es gibt genau ein Standard-Layout: die anderen Flags loeschen.
            andere = (
                await session.execute(select(Layout).where(Layout.id != layout_id, Layout.ist_standard.is_(True)))
            ).scalars().all()
            for a in andere:
                a.ist_standard = False
                session.add(a)
        layout.ist_standard = eingabe.ist_standard
    session.add(layout)
    await session.commit()
    await session.refresh(layout)
    return wrap(layout.model_dump())


@router.post("/{layout_id}/telefon-vorlage")
async def telefon_vorlage(layout_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    """Telefon-Layout des Profils auf die Vorlage zurücksetzen."""
    layout = await session.get(Layout, layout_id)
    if layout is None:
        raise HTTPException(status_code=404, detail="Layout nicht gefunden")
    layout.telefon = telefon_katalog.vorlage(layout.name).model_dump()
    session.add(layout)
    await session.commit()
    await session.refresh(layout)
    return wrap(layout.model_dump())


@router.delete("/{layout_id}")
async def loeschen(layout_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    layout = await session.get(Layout, layout_id)
    if layout is not None:
        await session.delete(layout)
        await session.commit()
    return wrap({"geloescht": True})
