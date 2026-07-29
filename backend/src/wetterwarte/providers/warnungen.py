"""Amtliche Warnungen (DWD) - vorerst ueber Bright Sky, spaeter eigener Ingester."""

import httpx

from ..config import settings

_STUFE = {"minor": 1, "moderate": 2, "severe": 3, "extreme": 4}


def _zeitraum(onset: str | None, expires: str | None) -> str:
    if onset and expires and onset[:10] == expires[:10]:
        return f"{onset[11:16]} - {expires[11:16]} Uhr"
    teile = []
    if onset:
        teile.append(f"ab {onset[8:10]}.{onset[5:7]}. {onset[11:16]}")
    if expires:
        teile.append(f"bis {expires[8:10]}.{expires[5:7]}. {expires[11:16]}")
    return " ".join(teile)


async def hole(lat: float, lon: float) -> list[dict]:
    params = {"lat": lat, "lon": lon}
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.bright_sky_base}/alerts", params=params)
        antwort.raise_for_status()
        alarme = antwort.json().get("alerts") or []

    ergebnis = []
    for a in alarme:
        titel = a.get("event_de") or a.get("headline_de") or "Wetterwarnung"
        ergebnis.append({
            "stufe": _STUFE.get(a.get("severity", "minor"), 1),
            "titel": titel,
            "zeit": _zeitraum(a.get("onset"), a.get("expires")),
        })
    return ergebnis
