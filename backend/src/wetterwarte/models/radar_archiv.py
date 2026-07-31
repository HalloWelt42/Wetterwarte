"""Historisch gespeicherte Radar-Frames (gerendertes PNG je Messzeitpunkt).

So laesst sich das Radar spaeter ueber das kurze DWD-Live-Fenster hinaus in die
Vergangenheit zurueckblaettern. Optional (per Schalter) und mit Aufbewahrungsdauer."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class RadarArchivFrame(SQLModel, table=True):
    frame_id: str = Field(primary_key=True)  # z.B. "ry-2607311335"
    zeit: datetime = Field(index=True)  # naive UTC des Messzeitpunkts
    png: bytes  # gerendertes Overlay-Bild (RGBA-PNG)
    angelegt: datetime = Field(default_factory=datetime.utcnow)
