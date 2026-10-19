"""Ein einzelner aufgezeichneter Messwert (Zeitreihe fuer das Langzeit-Archiv)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index
from sqlmodel import Field, SQLModel


class Messwert(SQLModel, table=True):
    # Je Ort, Größe und Zeitpunkt genau ein Wert; der Index trägt zugleich alle Abfragen je Ort.
    __table_args__ = (Index("uq_messwert_ort_variable_zeit", "ort", "variable", "zeit", unique=True),)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    ort: str
    zeit: datetime = Field(sa_type=DateTime(timezone=True), index=True)
    variable: str
    wert: float
