"""Open-Meteo-Provider: holt echte Wetterdaten und bringt sie in die App-Form.

Die Basis-URL ist konfigurierbar (settings.open_meteo_base). Vorerst der
oeffentliche Dienst; spaeter zeigt sie auf den lokal gespiegelten Dienst - die
Form der Antwort bleibt gleich.
"""

from datetime import UTC, date, datetime

import httpx

from ..config import settings
from ..gemeinsam import wetterbild
from ..zeit import jetzt

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
    """WMO-Wettercode zu (Meteocon-Name, deutscher Text), aus gemeinsam/wettercodes.json."""
    return wetterbild(code, tag)


def jetzt_index(zeiten: list[str], aktuell: str) -> int:
    """Index der Stunde (oder Viertelstunde), in die der aktuelle Zeitpunkt fällt."""
    marke = aktuell[:13]
    for i, t in enumerate(zeiten):
        if t[:13] == marke:
            return i
    return 0


def viertel_index(zeiten: list[str], aktuell: str) -> int:
    """Index der laufenden Viertelstunde: letzter Zeitpunkt, der nicht nach `aktuell` liegt."""
    index = 0
    for i, t in enumerate(zeiten):
        if t <= aktuell:
            index = i
    return index


async def historie(lat: float, lon: float, tage: int = 30) -> list[tuple[datetime, float]]:
    """Stündliche Temperatur der letzten `tage` Tage (für die Erst-Befüllung des Archivs).

    Zeiten in UTC; nur Vergangenes, denn die Antwort enthält auch die kommenden Stunden des
    laufenden Tags, und das sind Vorhersagen, keine Messwerte."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "past_days": tage,
        "forecast_days": 1,
        "timezone": "GMT",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        antwort = await client.get(f"{settings.open_meteo_base}/forecast", params=params)
        antwort.raise_for_status()
        h = antwort.json()["hourly"]
    grenze = jetzt()
    reihe = []
    for t, w in zip(h["time"], h["temperature_2m"], strict=False):
        zeit = datetime.fromisoformat(t).replace(tzinfo=UTC)
        if w is not None and zeit <= grenze:
            reihe.append((zeit, float(w)))
    return reihe


# Alles, was Desktop, Telefon und Aufzeichnung brauchen, in einem Abruf. Die Zeiten kommen in
# der Ortszeit des Orts (timezone=auto) ohne Versatz; die Zeitzone steht in "timezone".
_STUNDEN = (
    "temperature_2m,apparent_temperature,weather_code,precipitation_probability,precipitation,visibility,"
    "pressure_msl,is_day,wind_speed_10m,wind_gusts_10m,wind_direction_10m,uv_index,relative_humidity_2m,dew_point_2m,cloud_cover"
)
_TAGE = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,"
    "sunrise,sunset,daylight_duration,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max"
)


async def hole(lat: float, lon: float) -> dict:
    """Rohantwort von Open-Meteo (JSON) für einen Ort: aktuell, Stunden (24 h zurück bis 72 h voraus),
    7 Tage, 15-Minuten-Niederschlag für die nächsten 4 Stunden."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,"
            "wind_speed_10m,wind_direction_10m,wind_gusts_10m,pressure_msl,cloud_cover,dew_point_2m,uv_index,is_day,"
            "precipitation"
        ),
        "hourly": _STUNDEN,
        "minutely_15": "precipitation",
        "forecast_minutely_15": 16,
        "daily": _TAGE,
        # auto = Zeiten in der LOKALEN Zeitzone des Ortes, sonst stimmen Sonnenzeiten fuer ferne Orte nicht.
        "timezone": "auto",
        "forecast_days": 7,
        "past_hours": 24,  # der ganze heutige Tag (z. B. für die Uhrzeit des UV-Höchstwerts)
        "forecast_hours": 72,  # Stunden: 24 zurück, 72 voraus (ohne Angabe wären es 16 Tage)
        "wind_speed_unit": "kmh",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.open_meteo_base}/forecast", params=params)
        antwort.raise_for_status()
        return antwort.json()


def messwerte(d: dict) -> dict[str, float]:
    """Aktuelle Werte ungerundet, so wie die Aufzeichnung sie speichert."""
    c = d["current"]
    return {
        "temperatur": float(c["temperature_2m"]),
        "feuchte": float(c["relative_humidity_2m"]),
        "wind": float(c["wind_speed_10m"]),
        "druck": float(c["pressure_msl"]),
    }


async def komplett(lat: float, lon: float, name: str, region: str) -> dict:
    """Anzeigeform für den Desktop und die Kompat-Schicht, direkt von der Quelle."""
    return darstellung(await hole(lat, lon), name, region, lat, lon)


def darstellung(d: dict, name: str, region: str, lat: float, lon: float) -> dict:
    """Rohantwort in die Anzeigeform der Desktop-Kacheln bringen."""
    c = d["current"]
    tag = bool(c["is_day"])
    icon, text = _zustand(int(c["weather_code"]), tag)

    h = d["hourly"]
    idx = jetzt_index(h["time"], c["time"])
    sicht_m = h["visibility"][idx] if h.get("visibility") else None

    aktuell = {
        "temperatur": round(c["temperature_2m"]),
        "tempKlasse": _temp_klasse(c["temperature_2m"]),
        "gefuehlt": round(c["apparent_temperature"]),
        "tageshoch": round(d["daily"]["temperature_2m_max"][0]),
        "zustandText": text,
        "icon": icon,
        "weatherCode": int(c["weather_code"]),
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
        druck_h = h.get("pressure_msl")
        stunden.append({
            "zeit": "jetzt" if i == idx else h["time"][i][11:13],
            "icon": icon_h,
            "temp": round(h["temperature_2m"][i]),
            "tempKlasse": _temp_klasse(h["temperature_2m"][i]),
            "regen": h["precipitation_probability"][i] or 0,
            "druck": round(druck_h[i]) if druck_h and druck_h[i] is not None else None,
        })

    mm = d.get("minutely_15") or {}
    nowcast = None
    if mm.get("time"):
        i15 = viertel_index(mm["time"], c["time"])
        werte = [w or 0 for w in mm["precipitation"][i15 : i15 + 12]]
        maxw = max(werte) if werte else 0
        balken = [round(w / maxw * 100) if maxw > 0 else 3 for w in werte]
        minuten = next((i * 15 for i, w in enumerate(werte) if w >= 0.1), None)
        if minuten == 0:
            text = "Regen jetzt"
        elif minuten:
            text = f"Regen in {minuten} Minuten"
        else:
            text = "Kein Regen in den nächsten 3 Stunden"
        nowcast = {"text": text, "balken": balken}

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
        "zeitzone": d.get("timezone", ""),
        "aktuell": aktuell,
        "stunden": stunden,
        "tage": tage,
        "sonne": sonne,
        "nowcast": nowcast,
    }


async def zeitzone_fuer(lat: float, lon: float) -> str:
    """IANA-Zeitzone zu Koordinaten (Open-Meteo loest sie via timezone=auto auf).

    Fuer den Backfill der Ortsliste - schlanke Abfrage nur fuer das timezone-Feld.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "timezone": "auto",
        "forecast_days": 1,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        antwort = await client.get(f"{settings.open_meteo_base}/forecast", params=params)
        antwort.raise_for_status()
        return antwort.json().get("timezone", "")
