"""Amtliche Warnungen (DWD) - vorerst ueber Bright Sky, spaeter eigener Ingester.

Die Quelle liefert Zeiten mit Versatz in der angefragten Zeitzone (die des Orts). Gespeichert
und weitergegeben werden Rohwerte; die Textform für den Desktop entsteht in `zeitraum`."""

from datetime import datetime

import httpx

from ..config import settings
from ..zeit import jetzt, zone

_STUFE = {"minor": 1, "moderate": 2, "severe": 3, "extreme": 4}


async def hole(lat: float, lon: float, zeitzone: str) -> list[dict]:
    """Gültige Warnungen am Ort, höchste Stufe zuerst. Zeiten als ISO 8601 mit Versatz."""
    params = {"lat": lat, "lon": lon, "tz": zone(zeitzone).key}
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.bright_sky_base}/alerts", params=params)
        antwort.raise_for_status()
        alarme = antwort.json().get("alerts") or []

    ergebnis = []
    for a in alarme:
        ergebnis.append({
            "stufe": _STUFE.get(a.get("severity", "minor"), 1),
            "ereignis": a.get("event_de") or a.get("headline_de") or "Wetterwarnung",
            "ueberschrift": a.get("headline_de") or "",
            "beschreibung": a.get("description_de") or "",
            "von": a.get("onset"),
            "bis": a.get("expires"),
        })
    ergebnis.sort(key=lambda w: (-w["stufe"], w["von"] or ""))
    return ergebnis


def zeitraum(von: str | None, bis: str | None, zeitzone: str) -> str:
    """Kurzer Zeitraum in Ortszeit, z. B. "17:00 - 21:00 Uhr" oder "ab 19.10. 17:00 bis 20.10. 06:00"."""
    z = zone(zeitzone)
    a = datetime.fromisoformat(von).astimezone(z) if von else None
    e = datetime.fromisoformat(bis).astimezone(z) if bis else None
    heute = jetzt().astimezone(z).date()
    if a and e and a.date() == e.date():
        tag = "" if a.date() == heute else f"{a:%d.%m.} "
        return f"{tag}{a:%H:%M} - {e:%H:%M} Uhr"
    teile = []
    if a:
        teile.append(f"ab {a:%d.%m.} {a:%H:%M}")
    if e:
        teile.append(f"bis {e:%d.%m.} {e:%H:%M}")
    return " ".join(teile)


def darstellung(warnungen: list[dict], zeitzone: str) -> list[dict]:
    """Form der Desktop-Kachel: Stufe, Titel, Zeittext (plus die Rohfelder)."""
    return [{**w, "titel": w["ereignis"], "zeit": zeitraum(w["von"], w["bis"], zeitzone)} for w in warnungen]
