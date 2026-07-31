"""Gespeicherte Klima-Normale je Ort (als JSON), damit alte Klimadaten erhalten
bleiben und nicht bei jedem Aufruf neu berechnet werden muessen."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class KlimaNormale(SQLModel, table=True):
    ort: str = Field(primary_key=True)  # Ort-Slug
    daten: str  # JSON der Monatsnormale (siehe providers/klima.py)
    stand: datetime = Field(default_factory=datetime.now)
