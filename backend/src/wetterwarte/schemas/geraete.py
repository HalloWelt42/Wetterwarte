"""Ein- und Ausgaben der Geräte-API (routers/geraete.py, docs/WARNUNGEN.md)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..ansagen import katalog
from .lage import Meldeart


def _optionen(name: str) -> list[int]:
    return [o["wert"] for o in katalog()["optionen"][name]]


def _vorgabe() -> dict:
    return katalog()["optionen"]["vorgabe"]


class Nachtruhe(BaseModel):
    an: bool = Field(default_factory=lambda: _vorgabe()["nachtruhe"]["an"])
    von: int = Field(default_factory=lambda: _vorgabe()["nachtruhe"]["von"], ge=0, le=23)
    bis: int = Field(default_factory=lambda: _vorgabe()["nachtruhe"]["bis"], ge=0, le=23)
    ab_stufe: int = Field(default_factory=lambda: _vorgabe()["nachtruhe"]["ab_stufe"], ge=1, le=4)


class Meldeeinstellungen(BaseModel):
    """Was ein Gerät gemeldet haben will. Erlaubte Werte und Vorgaben stehen in gemeinsam/meldungen.json."""

    orte: list[str] = Field(default_factory=list, max_length=20)  # Orte für Mitteilungen (Slugs)
    arten: list[Meldeart] = Field(default_factory=lambda: list(_vorgabe()["arten"]))
    vorlauf_min: int = Field(default_factory=lambda: _vorgabe()["vorlauf_min"])
    niederschlag_ab: int = Field(default_factory=lambda: _vorgabe()["niederschlag_ab"])  # kleinster Rang
    wind_ab: int = Field(default_factory=lambda: _vorgabe()["wind_ab"])  # kleinster Rang
    nachtruhe: Nachtruhe = Field(default_factory=Nachtruhe)

    @field_validator("vorlauf_min", "niederschlag_ab", "wind_ab")
    @classmethod
    def _erlaubt(cls, wert: int, info) -> int:  # noqa: ANN001
        erlaubt = _optionen(info.field_name)
        if wert not in erlaubt:
            raise ValueError(f"erlaubt sind {erlaubt}")
        return wert


class PushAbo(BaseModel):
    """Abo des Browsers (PushSubscription.toJSON())."""

    endpoint: str = Field(pattern=r"^https://", max_length=2000)
    keys: dict[str, str]

    @field_validator("keys")
    @classmethod
    def _schluessel(cls, keys: dict[str, str]) -> dict[str, str]:
        if not keys.get("p256dh") or not keys.get("auth"):
            raise ValueError("p256dh und auth fehlen")
        return keys


class GeraetAnlage(BaseModel):
    ort: str | None = None  # Startort: vorgewählt für Mitteilungen


class Protokolleintrag(BaseModel):
    zeit: datetime
    kanal: str
    ort: str
    art: str
    stufe: int
    titel: str
    text: str
    zugestellt: bool


class GeraetAntwort(BaseModel):
    id: str
    einstellungen: Meldeeinstellungen
    push: bool  # ein Push-Abo ist hinterlegt
    protokoll: list[Protokolleintrag]


class Ansage(BaseModel):
    """Eine Meldung zum Sprechen (Kanal ansage) oder Senden (push)."""

    art: Meldeart
    schluessel: str
    stufe: int
    titel: str
    text: str
    bausteine: list[str]
    entwarnung: bool = False
