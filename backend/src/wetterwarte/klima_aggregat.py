"""Verdichtet die aufgezeichneten Messwerte zu Monatsaggregaten je Ort/Variable/Jahr.

Die Aggregate liegen dauerhaft in der Datenbank (Tabelle KlimaAggregat) und werden
periodisch vom Recorder sowie bei Bedarf beim Abruf aufgefrischt. Der Upsert nutzt
die eindeutige Spaltenkombination (Ort, Variable, Jahr, Monat).
"""

from datetime import datetime

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import SessionLocal
from .models.klima_aggregat import KlimaAggregat
from .models.messwert import Messwert


# Zeilen je Upsert-Batch. Pro Zeile bindet asyncpg 11 Parameter; das Limit liegt bei
# 32767 pro Statement, 1000 Zeilen (11000 Parameter) bleiben klar darunter.
_BATCH = 1000


async def aktualisiere(orte: list[str] | None = None, seit: datetime | None = None) -> int:
    """Monatsaggregate aus der Messwert-Tabelle neu berechnen und upserten.

    Optional auf bestimmte Orte begrenzen (guenstiger Scan beim Abruf eines Ortes)
    und/oder auf einen Zeitraum ab ``seit`` (z. B. nur laufender Monat im Recorder-Takt,
    damit die Kosten nicht mit der Archivgroesse wachsen). Liefert die Anzahl der
    geschriebenen (Ort, Variable, Jahr, Monat)-Zeilen.
    """
    jahr_e = cast(func.extract("year", Messwert.zeit), Integer).label("jahr")
    monat_e = cast(func.extract("month", Messwert.zeit), Integer).label("monat")
    stmt = select(
        Messwert.ort,
        Messwert.variable,
        jahr_e,
        monat_e,
        func.avg(Messwert.wert).label("mittel"),
        func.min(Messwert.wert).label("minimum"),
        func.max(Messwert.wert).label("maximum"),
        func.sum(Messwert.wert).label("summe"),
        func.count(Messwert.wert).label("anzahl"),
    ).group_by(Messwert.ort, Messwert.variable, jahr_e, monat_e)
    if orte:
        stmt = stmt.where(Messwert.ort.in_(orte))
    if seit is not None:
        stmt = stmt.where(Messwert.zeit >= seit)

    async with SessionLocal() as session:
        zeilen = (await session.execute(stmt)).all()
        if not zeilen:
            return 0
        stand = datetime.now()
        werte = [
            {
                "ort": r.ort,
                "variable": r.variable,
                "jahr": int(r.jahr),
                "monat": int(r.monat),
                "mittel": float(r.mittel),
                "minimum": float(r.minimum),
                "maximum": float(r.maximum),
                "summe": float(r.summe),
                "anzahl": int(r.anzahl),
                "stand": stand,
            }
            for r in zeilen
        ]
        # In Batches upserten, damit das asyncpg-Parameterlimit nie erreicht wird.
        for start in range(0, len(werte), _BATCH):
            teil = werte[start : start + _BATCH]
            ins = pg_insert(KlimaAggregat).values(teil)
            upsert = ins.on_conflict_do_update(
                constraint="uq_klima_aggregat",
                set_={
                    "mittel": ins.excluded.mittel,
                    "minimum": ins.excluded.minimum,
                    "maximum": ins.excluded.maximum,
                    "summe": ins.excluded.summe,
                    "anzahl": ins.excluded.anzahl,
                    "stand": ins.excluded.stand,
                },
            )
            await session.execute(upsert)
        await session.commit()
        return len(werte)


async def jahre(ort: str) -> list[int]:
    """Alle Jahre, fuer die ein Ort aggregierte Messwerte hat (aufsteigend)."""
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                select(KlimaAggregat.jahr).where(KlimaAggregat.ort == ort).distinct().order_by(KlimaAggregat.jahr)
            )
        ).scalars().all()
    return list(rows)


async def variablen(ort: str) -> list[str]:
    """Alle Variablen, fuer die ein Ort aggregierte Messwerte hat."""
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                select(KlimaAggregat.variable).where(KlimaAggregat.ort == ort).distinct()
            )
        ).scalars().all()
    return list(rows)


async def monate(ort: str, variable: str, jahr: int) -> list[dict]:
    """Monatsaggregate eines Ortes fuer eine Variable in einem Jahr (Monat 1..12)."""
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                select(KlimaAggregat)
                .where(KlimaAggregat.ort == ort, KlimaAggregat.variable == variable, KlimaAggregat.jahr == jahr)
                .order_by(KlimaAggregat.monat)
            )
        ).scalars().all()
    return [
        {
            "monat": r.monat,
            "mittel": round(r.mittel, 1),
            "minimum": round(r.minimum, 1),
            "maximum": round(r.maximum, 1),
            "summe": round(r.summe, 1),
            "anzahl": r.anzahl,
        }
        for r in rows
    ]
