"""Antwort des Telefon-Endpunkts /wetter/kompakt/{ort}: Rohwerte statt Anzeigeform.

Zahlen ungerundet, Zeiten als Zeitpunkte mit Versatz, Wettercodes nach WMO. Gestaltung
(Symbole, Farben, Texte) entsteht erst in der Oberfläche. Jeder Bereich hat Status und Stand;
fehlt ein Bereich, ist sein Feld null und sein Status "fehlt"."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class KOrt(BaseModel):
    slug: str
    name: str
    region: str
    lat: float
    lon: float
    zeitzone: str


class Bereich(BaseModel):
    status: Literal["ok", "alt", "fehlt"]
    stand: datetime | None


class Jetzt(BaseModel):
    zeit: datetime
    temp: float
    gefuehlt: float
    code: int
    tag: bool
    feuchte: float
    taupunkt: float
    druck: float
    druck_tendenz: float | None  # Änderung in hPa über die letzten 3 Stunden
    sicht_km: float | None
    bewoelkung: float
    wind: float
    boeen: float
    wind_grad: float
    uv: float
    regen_mm: float


class Stunde(BaseModel):
    zeit: datetime
    temp: float
    gefuehlt: float
    code: int
    tag: bool
    regen_wahrsch: float | None
    regen_mm: float
    wind: float
    boeen: float
    wind_grad: float
    uv: float
    feuchte: float
    taupunkt: float
    druck: float
    sicht_km: float | None
    bewoelkung: float


class Tag(BaseModel):
    datum: date
    code: int
    hoch: float
    tief: float
    regen_wahrsch: float | None
    regen_mm: float
    wind_max: float
    boeen_max: float
    uv_max: float
    sonnenaufgang: datetime | None
    sonnenuntergang: datetime | None
    tageslaenge_s: float


class Regen(BaseModel):
    """Kurzfrist für 2 Stunden in Viertelstunden (mm/h), aus dem Vorhersagemodell."""

    schritt_min: int = 15
    werte: list[float]
    beginn_min: int | None  # Minuten bis Regen (0 = regnet), None = trocken
    ende_min: int | None  # Minuten bis Regenende innerhalb der 2 Stunden
    max_mm_h: float
    quelle: Literal["modell"] = "modell"


class Warnung(BaseModel):
    stufe: int
    ereignis: str
    ueberschrift: str
    beschreibung: str
    von: datetime | None
    bis: datetime | None


class Einschlag(BaseModel):
    km: float
    grad: float
    zeit: datetime


class Blitze(BaseModel):
    anzahl_30: int
    anzahl_60: int
    naechster_km: float | None
    naechster_grad: float | None
    zuletzt: datetime | None
    einschlaege: list[Einschlag]  # letzte 30 Minuten, neueste zuerst


class Schadstoff(BaseModel):
    schluessel: str
    titel: str
    wert: float
    einheit: str


class Luft(BaseModel):
    index: int  # europäischer Luftqualitätsindex
    stufe: str
    schadstoffe: list[Schadstoff]


class Pollenart(BaseModel):
    schluessel: str
    titel: str
    heute: float  # DWD-Stufe 0 bis 3 in halben Schritten, -1 = keine Angabe
    morgen: float
    uebermorgen: float


class Pollen(BaseModel):
    region: str
    arten: list[Pollenart]


class Kompakt(BaseModel):
    ort: KOrt
    zeit: datetime  # Zeitpunkt der Antwort
    bereiche: dict[str, Bereich]
    jetzt: Jetzt | None
    stunden: list[Stunde]  # ab 6 Stunden zurück bis 48 Stunden voraus
    jetzt_index: int  # Index der laufenden Stunde in stunden
    tage: list[Tag]
    regen: Regen | None
    warnungen: list[Warnung] | None
    blitze: Blitze | None
    luft: Luft | None
    pollen: Pollen | None
