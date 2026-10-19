"""Einheitlicher Antwort-Umschlag: { data, meta }.

meta trägt die Fassung des Servers und bei Datenbereichen zusätzlich Status und Stand
(ok, alt, fehlt), damit die Oberfläche ehrlich zeigen kann, wie verlässlich ein Wert ist."""

from ..bereiche import Ergebnis
from ..config import settings


def wrap(data: object, *, ergebnis: Ergebnis | None = None) -> dict:
    meta: dict = {"version": settings.version}
    if ergebnis is not None:
        meta.update(ergebnis.meta())
    return {"data": data, "meta": meta}
