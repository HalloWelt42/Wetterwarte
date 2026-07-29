"""Wetter-Endpunkte.

Vorerst Platzhalterdaten, damit das Frontend gegen eine stabile Form entwickeln
kann. Die echte Anbindung (eigener DWD-Ingester und lokal gespiegeltes Open-Meteo)
folgt in einer spaeteren Ausbaustufe und ersetzt nur die Datenherkunft, nicht die Form.
"""

from fastapi import APIRouter

from ..schemas.envelope import wrap

router = APIRouter(prefix="/weather", tags=["weather"])


def _platzhalter_komplett(ort: str) -> dict:
    return {
        "ort": {"name": ort, "region": "Sachsen-Anhalt", "lat": 51.05, "lon": 12.14},
        "aktuell": {
            "temperatur": 24,
            "gefuehlt": 26,
            "zustand": "wolkig",
            "zustand_text": "Wolkig, später Schauer",
            "icon": "partly-cloudy-day",
            "feuchte": 68,
            "wind": 14,
            "wind_richtung": 315,
            "boeen": 32,
            "druck": 1012,
            "sicht": 24,
            "taupunkt": 17,
            "bewoelkung": 60,
            "uv": 6,
        },
        "sonne": {"aufgang": "05:42", "untergang": "21:18", "tageslaenge": "15:36"},
        "mond": {"phase": "zunehmend", "beleuchtung": 78, "icon": "moon-waxing-gibbous"},
    }


@router.get("/complete/{ort}")
async def complete(ort: str) -> dict:
    """Alles zu einem Ort in einer Antwort (Platzhalter)."""
    return wrap(_platzhalter_komplett(ort), platzhalter=True)
