"""Einmalige Datenmigrationen, idempotent ueber Einstellung-Flags.

Wahrheit liegt in der Datenbank; jede Migration laeuft genau einmal und ist
gefahrlos, falls sie doch erneut startet (Flag-Guard)."""

import uuid

from sqlmodel import select

from .db import SessionLocal
from .models.einstellung import Einstellung
from .models.layout import Layout


async def _flag_gesetzt(schluessel: str) -> bool:
    async with SessionLocal() as session:
        row = await session.get(Einstellung, schluessel)
        return bool(row and row.wert == "1")


async def _setze_flag(schluessel: str) -> None:
    async with SessionLocal() as session:
        row = await session.get(Einstellung, schluessel)
        if row is not None:
            row.wert = "1"
        else:
            session.add(Einstellung(schluessel=schluessel, wert="1"))
        await session.commit()


async def migriere_tile_ids() -> None:
    """Alle Kachel-IDs in den Layouts auf global eindeutige UUIDs umstellen.

    Fruehere Profile vergaben positions-/index-basierte IDs (typ-x-y, typ-i), die
    sich ueber Profile hinweg wiederholten. Dadurch koppelten sich Profile ueber
    gleiche IDs (Groesse/Einstellungen wanderten zwischen ihnen). typ, Position,
    Groesse und conf bleiben erhalten - nur die id wird neu und eindeutig."""
    if await _flag_gesetzt("tile_ids_uuid_migriert"):
        return
    async with SessionLocal() as session:
        layouts = (await session.execute(select(Layout))).scalars().all()
        for layout in layouts:
            neu = []
            for kachel in layout.daten or []:
                if isinstance(kachel, dict):
                    typ = kachel.get("typ") or "kachel"
                    neu.append({**kachel, "id": f"{typ}-{uuid.uuid4()}"})
                else:
                    neu.append(kachel)
            layout.daten = neu  # Neuzuweisung -> SQLAlchemy erkennt die JSON-Aenderung
        await session.commit()
    await _setze_flag("tile_ids_uuid_migriert")
