"""Endpunkte fuer benannte Dashboard-Layouts."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..db import get_session
from ..models.layout import Layout
from ..schemas.envelope import wrap

router = APIRouter(prefix="/layouts", tags=["layouts"])


class LayoutEingabe(BaseModel):
    name: str | None = None
    daten: list | None = None
    ist_standard: bool | None = None


@router.get("")
async def liste(session: AsyncSession = Depends(get_session)) -> dict:
    ergebnis = await session.execute(select(Layout))
    return wrap([l.model_dump() for l in ergebnis.scalars().all()])


@router.post("")
async def anlegen(eingabe: LayoutEingabe, session: AsyncSession = Depends(get_session)) -> dict:
    layout = Layout(name=eingabe.name or "Neues Layout", daten=eingabe.daten or [])
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
    if eingabe.ist_standard is not None:
        layout.ist_standard = eingabe.ist_standard
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
