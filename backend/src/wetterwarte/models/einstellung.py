"""Kleiner Schluessel-Wert-Speicher fuer globale Einstellungen (z.B. Radar-Archiv).

Bewusst generisch gehalten, damit weitere globale Schalter ohne Schema-Aenderung
hinzukommen koennen (Wahrheit im Backend, im UI sichtbar/einstellbar)."""

from sqlmodel import Field, SQLModel


class Einstellung(SQLModel, table=True):
    schluessel: str = Field(primary_key=True)
    wert: str = ""
