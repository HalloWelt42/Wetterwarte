"""Dateien, die Backend und Oberfläche teilen (Ordner gemeinsam/ im Projektwurzelverzeichnis):
Telefon-Kachelkatalog und Wettercodes. Die Oberfläche baut sie beim Bau ein, das Backend liest
sie hier. Im Container nennt WETTERWARTE_GEMEINSAM den mitgebauten Ordner (backend/Dockerfile)."""

import json
import os
from functools import cache
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2]
_ORDNER = Path(os.environ.get("WETTERWARTE_GEMEINSAM") or _BACKEND.parent / "gemeinsam")


@cache
def lies(name: str) -> dict:
    return json.loads((_ORDNER / name).read_text(encoding="utf-8"))


def telefon_katalog() -> dict:
    return lies("telefon-katalog.json")


@cache
def _codes() -> dict[int, dict]:
    tabelle: dict[int, dict] = {}
    for gruppe in lies("wettercodes.json")["gruppen"]:
        for code in gruppe["codes"]:
            tabelle[code] = gruppe
    return tabelle


def wetterbild(code: int, tag: bool) -> tuple[str, str]:
    """WMO-Code zu (Meteocon-Name, deutscher Text)."""
    gruppe = _codes().get(code) or lies("wettercodes.json")["sonst"]
    return (gruppe["tag"] if tag else gruppe["nacht"], gruppe["text"])
