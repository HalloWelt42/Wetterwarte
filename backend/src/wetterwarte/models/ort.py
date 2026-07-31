"""Ein gespeicherter Ort.

Die Ortsliste ist datengetrieben: der Nutzer fuegt Orte per Suche hinzu, sie
liegen in der Datenbank (Quelle der Wahrheit), nicht im Quellcode.
"""

import uuid

from sqlmodel import Field, SQLModel


class Ort(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    region: str = ""
    land: str = ""
    lat: float
    lon: float
    zeitzone: str = ""  # IANA-Zeitzone (fuer Uhr/Sonne/Mond je Ort)
    reihenfolge: int = 0
    ist_start: bool = False
