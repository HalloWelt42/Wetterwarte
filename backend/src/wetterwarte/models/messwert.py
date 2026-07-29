"""Ein einzelner aufgezeichneter Messwert (Zeitreihe fuer das Langzeit-Archiv)."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Messwert(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    ort: str = Field(index=True)
    zeit: datetime = Field(index=True)
    variable: str = Field(index=True)
    wert: float
