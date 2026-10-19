"""Historisch gespeicherte Radar-Frames (gerendertes PNG je Messzeitpunkt).

So laesst sich das Radar spaeter ueber das kurze DWD-Live-Fenster hinaus in die
Vergangenheit zurueckblaettern. Optional (per Schalter) und mit Aufbewahrungsdauer."""

from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from ..zeit import jetzt


class RadarArchivFrame(SQLModel, table=True):
    frame_id: str = Field(primary_key=True)  # z.B. "ry-2607311335"
    zeit: datetime = Field(index=True, sa_type=DateTime(timezone=True))  # Messzeitpunkt
    png: bytes  # gerendertes Overlay-Bild (RGBA-PNG)
    angelegt: datetime = Field(default_factory=jetzt, sa_type=DateTime(timezone=True))
