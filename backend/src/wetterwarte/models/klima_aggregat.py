"""Aus den aufgezeichneten Messwerten aggregierte Monatswerte je Ort/Variable/Jahr.

Das ist die dauerhaft in der Datenbank gehaltene Verdichtung der Zeitreihe
(Mittel/Min/Max/Summe/Anzahl pro Monat). Daraus speist sich das Jahresmesswerte-
Diagramm, ohne bei jedem Aufruf die komplette Messwert-Tabelle zu durchrechnen.
"""

import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class KlimaAggregat(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("ort", "variable", "jahr", "monat", name="uq_klima_aggregat"),)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    ort: str = Field(index=True)
    variable: str = Field(index=True)
    jahr: int = Field(index=True)
    monat: int  # 1..12
    mittel: float
    minimum: float
    maximum: float
    summe: float
    anzahl: int
    stand: datetime = Field(default_factory=datetime.now)
