"""Klima-Normale aus dem Open-Meteo-Archiv (ERA5): Monatsmittel Temperatur +
mittlerer Monatsniederschlag ueber einen Referenzzeitraum.

Ergibt ein klassisches Klimadiagramm (12 Monate). Die Werte aendern sich nur
langsam; das Backend speichert sie und schreibt sie gelegentlich fort.
"""

from collections import defaultdict
from datetime import date

import httpx

ARCHIVE_BASE = "https://archive-api.open-meteo.com/v1/archive"
MONATE_KURZ = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


async def normalen(lat: float, lon: float, jahre: int = 15) -> dict:
    """Monatsnormale (Temperatur-Mittel, Niederschlags-Mittel) der letzten `jahre` Jahre."""
    heute = date.today()
    start = date(heute.year - jahre, 1, 1)
    ende = date(heute.year - 1, 12, 31)

    async with httpx.AsyncClient(timeout=45.0) as client:
        antwort = await client.get(
            ARCHIVE_BASE,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": start.isoformat(),
                "end_date": ende.isoformat(),
                "daily": "temperature_2m_mean,precipitation_sum",
                "timezone": "auto",
            },
        )
        antwort.raise_for_status()
        d = antwort.json()

    zeiten = d["daily"]["time"]
    temps = d["daily"]["temperature_2m_mean"]
    niederschlag = d["daily"]["precipitation_sum"]

    temp_summe: dict[int, float] = defaultdict(float)
    temp_zahl: dict[int, int] = defaultdict(int)
    nied_je_monat_jahr: dict[tuple[int, int], float] = defaultdict(float)

    for t, tm, nd in zip(zeiten, temps, niederschlag):
        monat = int(t[5:7])
        jahr = int(t[0:4])
        if tm is not None:
            temp_summe[monat] += tm
            temp_zahl[monat] += 1
        if nd is not None:
            nied_je_monat_jahr[(jahr, monat)] += nd

    nied_summe: dict[int, float] = defaultdict(float)
    nied_jahre: dict[int, int] = defaultdict(int)
    for (_jahr, monat), summe in nied_je_monat_jahr.items():
        nied_summe[monat] += summe
        nied_jahre[monat] += 1

    monate = []
    for m in range(1, 13):
        monate.append(
            {
                "monat": m,
                "kurz": MONATE_KURZ[m - 1],
                "temp": round(temp_summe[m] / temp_zahl[m], 1) if temp_zahl[m] else None,
                "niederschlag": round(nied_summe[m] / nied_jahre[m]) if nied_jahre[m] else None,
            }
        )

    jahres_temp = [x["temp"] for x in monate if x["temp"] is not None]
    jahres_nied = [x["niederschlag"] for x in monate if x["niederschlag"] is not None]
    return {
        "monate": monate,
        "von": start.year,
        "bis": ende.year,
        "jahresmittel_temp": round(sum(jahres_temp) / len(jahres_temp), 1) if jahres_temp else None,
        "jahresniederschlag": round(sum(jahres_nied)) if jahres_nied else None,
    }
