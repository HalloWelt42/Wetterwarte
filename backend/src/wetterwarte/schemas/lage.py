"""Lage am Ort: kommende und laufende Wetterereignisse (siehe lage.py und docs/WARNUNGEN.md)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Meldeart = Literal["warnung", "niederschlag", "gewitter", "wind"]
Quelle = Literal["radar", "vorhersage", "amtlich", "blitze"]


class Ereignis(BaseModel):
    art: Meldeart
    schluessel: str  # Episode: je Art höchstens eine kommende ("niederschlag"), Warnungen je Ereignis und Beginn
    klasse: str  # Klassenschlüssel aus gemeinsam/meldungen.json, bei Warnungen das Ereignis
    rang: int  # Stärke innerhalb der Art (stärker = größer)
    stufe: int  # 1 bis 4 nach dem Maßstab der amtlichen Warnstufen (3 = Unwetter)
    beginn: datetime | None
    laeuft: bool = False  # hat schon begonnen und wird nicht mehr angekündigt
    vorlauf_min: int | None = None  # Minuten bis zum Beginn
    vorlaufstufe: int | None = None  # Staffel der Ankündigung (360, 180, ... 15), None: sofort melden
    quelle: Quelle
    titel: str
    text: str  # Text der Mitteilung, Wort für Wort wie die Ansage
    bausteine: list[str]  # Satzschlüssel der Ansage
