"""Open-Meteo-Provider: holt echte Wetterdaten und bringt sie in die App-Form.

Die Basis-URL ist konfigurierbar (settings.open_meteo_base). Vorerst der
oeffentliche Dienst; spaeter zeigt sie auf den lokal gespiegelten Dienst - die
Form der Antwort bleibt gleich.
"""

from datetime import date

import httpx

from ..config import settings

_WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
_RICHTUNGEN = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]


def _himmelsrichtung(grad: float) -> str:
    return _RICHTUNGEN[round(grad / 45) % 8]


def _temp_klasse(t: float) -> str:
    if t < 0:
        return "t-frost"
    if t < 8:
        return "t-kalt"
    if t < 14:
        return "t-kuehl"
    if t < 20:
        return "t-mild"
    if t < 26:
        return "t-warm"
    if t < 32:
        return "t-heiss"
    return "t-extrem"


def _zustand(code: int, tag: bool) -> tuple[str, str]:
    """WMO-Wettercode zu (Meteocon-Name, deutscher Text)."""
    z = "day" if tag else "night"
    if code == 0:
        return (f"clear-{z}", "Klar")
    if code == 1:
        return (f"partly-cloudy-{z}", "Ueberwiegend klar")
    if code == 2:
        return (f"partly-cloudy-{z}", "Wolkig")
    if code == 3:
        return ("overcast-day" if tag else "overcast", "Bedeckt")
    if code in (45, 48):
        return (f"fog-{z}", "Nebel")
    if code in (51, 53, 55, 56, 57):
        return ("drizzle", "Nieselregen")
    if code in (61, 63, 65, 66, 67):
        return ("rain", "Regen")
    if code in (80, 81, 82):
        return ("rain", "Schauer")
    if code in (71, 73, 75, 77, 85, 86):
        return ("snow", "Schnee")
    if code == 95:
        return ("thunderstorms-day-rain" if tag else "thunderstorms-night", "Gewitter")
    if code in (96, 99):
        return ("thunderstorms-day-rain" if tag else "thunderstorms-night", "Gewitter mit Hagel")
    return ("cloudy", "Wechselnd bewoelkt")


def _jetzt_index(zeiten: list[str], jetzt: str) -> int:
    marke = jetzt[:13]
    for i, t in enumerate(zeiten):
        if t[:13] == marke:
            return i
    return 0


async def komplett(lat: float, lon: float, name: str, region: str) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,"
            "wind_speed_10m,wind_direction_10m,wind_gusts_10m,pressure_msl,cloud_cover,dew_point_2m,uv_index,is_day"
        ),
        "hourly": "temperature_2m,weather_code,precipitation_probability,visibility,is_day",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "timezone": "Europe/Berlin",
        "forecast_days": 7,
        "wind_speed_unit": "kmh",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.open_meteo_base}/forecast", params=params)
        antwort.raise_for_status()
        d = antwort.json()

    c = d["current"]
    tag = bool(c["is_day"])
    icon, text = _zustand(int(c["weather_code"]), tag)

    h = d["hourly"]
    idx = _jetzt_index(h["time"], c["time"])
    sicht_m = h["visibility"][idx] if h.get("visibility") else None

    aktuell = {
        "temperatur": round(c["temperature_2m"]),
        "tempKlasse": _temp_klasse(c["temperature_2m"]),
        "gefuehlt": round(c["apparent_temperature"]),
        "tageshoch": round(d["daily"]["temperature_2m_max"][0]),
        "zustandText": text,
        "icon": icon,
        "feuchte": round(c["relative_humidity_2m"]),
        "wind": round(c["wind_speed_10m"]),
        "windRichtung": _himmelsrichtung(c["wind_direction_10m"]),
        "windGrad": round(c["wind_direction_10m"]),
        "boeen": round(c.get("wind_gusts_10m") or 0),
        "druck": round(c["pressure_msl"]),
        "sicht": round(sicht_m / 1000) if sicht_m is not None else None,
        "taupunkt": round(c["dew_point_2m"]),
        "bewoelkung": round(c["cloud_cover"]),
        "uv": round(c.get("uv_index") or 0),
    }

    stunden = []
    for i in range(idx, min(idx + 18, len(h["time"]))):
        icon_h, _ = _zustand(int(h["weather_code"][i]), bool(h["is_day"][i]))
        stunden.append({
            "zeit": "jetzt" if i == idx else h["time"][i][11:13],
            "icon": icon_h,
            "temp": round(h["temperature_2m"][i]),
            "tempKlasse": _temp_klasse(h["temperature_2m"][i]),
            "regen": h["precipitation_probability"][i] or 0,
        })

    dl = d["daily"]
    hoch = [round(x) for x in dl["temperature_2m_max"]]
    tief = [round(x) for x in dl["temperature_2m_min"]]
    woche_max = max(hoch)
    woche_min = min(tief)
    spanne = max(1, woche_max - woche_min)
    tage = []
    for i in range(len(dl["time"])):
        icon_t, _ = _zustand(int(dl["weather_code"][i]), True)
        dt = date.fromisoformat(dl["time"][i])
        tage.append({
            "kurz": "Heute" if i == 0 else _WOCHENTAGE[dt.weekday()],
            "icon": icon_t,
            "hi": hoch[i],
            "lo": tief[i],
            "regen": dl["precipitation_probability_max"][i] or 0,
            "bandLinks": round((tief[i] - woche_min) / spanne * 100),
            "bandRechts": round((woche_max - hoch[i]) / spanne * 100),
        })

    sonne = {
        "aufgang": dl["sunrise"][0][11:16],
        "untergang": dl["sunset"][0][11:16],
    }

    return {
        "ort": {"name": name, "region": region, "lat": lat, "lon": lon},
        "aktuell": aktuell,
        "stunden": stunden,
        "tage": tage,
        "sonne": sonne,
    }
