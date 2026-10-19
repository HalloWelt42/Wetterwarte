"""Geräte, die Meldungen bekommen (docs/WARNUNGEN.md): Einstellungen, Push-Abo, Gedächtnis je Kanal und Ort,
Protokoll der gesendeten Mitteilungen."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel

from ..zeit import jetzt


class Geraet(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # Meldeeinstellungen (schemas/geraete.py), geprüft beim Schreiben
    einstellungen: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    # Push-Abo des Browsers; leer, solange das Gerät keine Mitteilungen will
    push_endpunkt: str | None = None
    push_p256dh: str | None = None
    push_auth: str | None = None
    erstellt: datetime = Field(default_factory=jetzt, sa_type=DateTime(timezone=True))
    gesehen: datetime = Field(default_factory=jetzt, sa_type=DateTime(timezone=True))


class Meldegedaechtnis(SQLModel, table=True):
    """Was ein Kanal eines Geräts zu einem Ort zuletzt gemeldet hat (melden.Erinnerung je Episodenschlüssel)."""

    geraet_id: str = Field(primary_key=True, foreign_key="geraet.id", ondelete="CASCADE")
    kanal: str = Field(primary_key=True)  # push | ansage
    ort: str = Field(primary_key=True)
    eintraege: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    aktualisiert: datetime = Field(default_factory=jetzt, sa_type=DateTime(timezone=True))


class Meldung(SQLModel, table=True):
    """Protokoll: jede gesendete Mitteilung und jede abgeholte Ansage."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    geraet_id: str = Field(index=True, foreign_key="geraet.id", ondelete="CASCADE")
    kanal: str
    ort: str
    art: str
    schluessel: str
    stufe: int
    titel: str
    text: str
    zeit: datetime = Field(default_factory=jetzt, index=True, sa_type=DateTime(timezone=True))
    zugestellt: bool = True
