"""Ein benanntes Dashboard-Layout (Kachel-Anordnung als JSON)."""

import uuid

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Layout(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    ist_standard: bool = False
    # Frei waehlbares Profil-Icon (Font-Awesome-Klasse, z.B. "fa-house"). Leer =
    # Standard nach Name.
    icon: str = ""
    # gridstack-Serialisierung: Liste von { id, x, y, w, h }
    daten: list = Field(default_factory=list, sa_column=Column(JSON))
    # Telefon-Layout dieses Profils: { kacheln: [{ id, typ, x, y, w, h, conf }] } im 3er-Raster.
    # Leer = Vorlage (siehe telefon.py).
    telefon: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
