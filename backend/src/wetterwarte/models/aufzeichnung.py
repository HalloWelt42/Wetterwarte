"""Aufzeichnungs-Auswahl: welcher Ort mit welchen Variablen dauerhaft archiviert wird.

Eine Zeile je Ort. Fehlt eine Zeile, gilt der Standard (aktiv, alle Variablen) -
so werden neue Orte automatisch mitgeschrieben, bis der Nutzer es aendert.
"""

from sqlmodel import Field, SQLModel


class AufzeichnungOrt(SQLModel, table=True):
    ort: str = Field(primary_key=True)  # Ort-Slug
    variablen: str = Field(default="temperatur,feuchte,wind,druck")  # aktive Variablen, kommagetrennt
    aktiv: bool = Field(default=True)
