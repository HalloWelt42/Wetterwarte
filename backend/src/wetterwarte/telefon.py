"""Telefon-Layouts: Katalog, Vorlage und Prüfung.

Der Katalog (telefon-katalog.json im Projektwurzelverzeichnis) ist die einzige Wahrheit über
die Telefon-Kacheltypen, ihre erlaubten Größen und Einstellungen. Die Oberfläche baut ihn beim
Bau ein, das Backend liest ihn hier und prüft jedes gespeicherte Layout dagegen."""

import json
import os
import uuid
from functools import cache
from pathlib import Path

from pydantic import BaseModel, Field

_BACKEND = Path(__file__).resolve().parents[2]
_KATALOGDATEI = Path(os.environ.get("WETTERWARTE_KATALOG_DATEI") or _BACKEND.parent / "telefon-katalog.json")


class TelefonKachel(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    typ: str
    x: int
    y: int
    w: int
    h: int
    conf: dict = Field(default_factory=dict)


class TelefonLayout(BaseModel):
    kacheln: list[TelefonKachel] = Field(default_factory=list, max_length=60)


@cache
def katalog() -> dict:
    return json.loads(_KATALOGDATEI.read_text(encoding="utf-8"))


def neue_id(typ: str) -> str:
    return f"{typ}-{uuid.uuid4()}"


def vorlage() -> TelefonLayout:
    """Vorlage für ein Profil ohne eigenes Telefon-Layout, mit frischen Kachel-IDs."""
    return TelefonLayout(kacheln=[TelefonKachel(id=neue_id(k["typ"]), **k) for k in katalog()["vorlage"]])


def _pruefe_conf(typ: str, conf: dict) -> None:
    einstellungen = {e["schluessel"]: e for e in katalog()["typen"][typ]["einstellungen"]}
    for schluessel, wert in conf.items():
        e = einstellungen.get(schluessel)
        if e is None:
            raise ValueError(f"{typ}: unbekannte Einstellung {schluessel}")
        erlaubt = {o["wert"] for o in e["optionen"]}
        if e["art"] == "auswahl" and wert not in erlaubt:
            raise ValueError(f"{typ}: {schluessel} = {wert} ist nicht vorgesehen")
        if e["art"] == "mehrfach" and (not isinstance(wert, list) or not set(wert) <= erlaubt):
            raise ValueError(f"{typ}: {schluessel} enthält nicht vorgesehene Werte")


def pruefe(layout: TelefonLayout) -> None:
    """Typ, Größe, Lage und Einstellungen jeder Kachel gegen den Katalog; keine Überlappung,
    keine doppelte ID. Wirft ValueError mit lesbarem Grund."""
    typen = katalog()["typen"]
    spalten = katalog()["spalten"]
    belegt: dict[tuple[int, int], str] = {}
    ids: set[str] = set()
    for k in layout.kacheln:
        if k.typ not in typen:
            raise ValueError(f"Unbekannter Kacheltyp {k.typ}")
        if f"{k.w}x{k.h}" not in typen[k.typ]["groessen"]:
            raise ValueError(f"{k.typ}: Größe {k.w}x{k.h} ist nicht vorgesehen")
        if k.x < 0 or k.y < 0 or k.x + k.w > spalten or k.y > 200:
            raise ValueError(f"{k.typ}: Lage {k.x}, {k.y} liegt außerhalb des Rasters")
        if k.id in ids:
            raise ValueError(f"Kachel-ID {k.id} kommt doppelt vor")
        ids.add(k.id)
        _pruefe_conf(k.typ, k.conf)
        for dx in range(k.w):
            for dy in range(k.h):
                feld = (k.x + dx, k.y + dy)
                if feld in belegt:
                    raise ValueError(f"{k.typ} überlappt {belegt[feld]} bei {feld[0]}, {feld[1]}")
                belegt[feld] = k.typ
