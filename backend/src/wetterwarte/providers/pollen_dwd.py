"""DWD-Pollenflug-Gefahrenindex (offizielle Quelle).

Quelle: https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json
Liefert je Region acht Pollenarten mit den Stufen Heute / Morgen / Uebermorgen.
Die passende Region wird ueber die kuerzeste Entfernung zu einem Regionszentrum
bestimmt (Haversine). Struktur bleibt stabil, damit ein spaeterer eigener
Ingester nur die Quelle, nicht die Form aendert.
"""

import math

import httpx

DWD_POLLEN_URL = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"

# DWD-Stufen (Rohwert -> numerisch + Text + Farbe).
STUFEN: dict[str, dict] = {
    "-1": {"value": -1, "label": "keine Daten", "color": "#9E9E9E"},
    "0": {"value": 0, "label": "keine", "color": "#4CAF50"},
    "0-1": {"value": 0.5, "label": "keine bis gering", "color": "#8BC34A"},
    "1": {"value": 1, "label": "gering", "color": "#CDDC39"},
    "1-2": {"value": 1.5, "label": "gering bis mittel", "color": "#FFEB3B"},
    "2": {"value": 2, "label": "mittel", "color": "#FFC107"},
    "2-3": {"value": 2.5, "label": "mittel bis hoch", "color": "#FF9800"},
    "3": {"value": 3, "label": "hoch", "color": "#F44336"},
}

# DWD-Schluessel -> Anzeigename (mit echten Umlauten).
ARTEN: dict[str, str] = {
    "Hasel": "Hasel",
    "Erle": "Erle",
    "Esche": "Esche",
    "Birke": "Birke",
    "Graeser": "Gräser",
    "Roggen": "Roggen",
    "Beifuss": "Beifuß",
    "Ambrosia": "Ambrosia",
}

# Original-Emojis je Art.
EMOJIS: dict[str, str] = {
    "Hasel": "🌰",
    "Erle": "🌳",
    "Esche": "🌲",
    "Birke": "🌳",
    "Graeser": "🌾",
    "Roggen": "🌾",
    "Beifuss": "🌿",
    "Ambrosia": "🌱",
}

# Stabiler Schluessel je Art (fuer Auswahl "meine Allergien").
SCHLUESSEL: dict[str, str] = {
    "Hasel": "hasel",
    "Erle": "erle",
    "Esche": "esche",
    "Birke": "birke",
    "Graeser": "graeser",
    "Roggen": "roggen",
    "Beifuss": "beifuss",
    "Ambrosia": "ambrosia",
}

# DWD-Regionen mit ungefaehrem Zentrum: (region_id, partregion_id, name, lat, lon).
REGIONEN: list[tuple[int, int, str, float, float]] = [
    (10, 11, "Schleswig-Holstein: Inseln und Marschen", 54.5, 8.8),
    (10, 12, "Schleswig-Holstein: Geest und Hamburg", 53.8, 9.8),
    (20, -1, "Mecklenburg-Vorpommern", 53.8, 12.5),
    (30, 31, "Niedersachsen: Westl./Bremen", 53.0, 8.0),
    (30, 32, "Niedersachsen: Östlich", 52.5, 10.0),
    (40, 41, "NRW: Rhein.-Westfäl. Tiefland", 51.5, 7.0),
    (40, 42, "NRW: Ostwestfalen", 52.0, 8.5),
    (40, 43, "NRW: Mittelgebirge", 51.0, 7.5),
    (50, -1, "Brandenburg und Berlin", 52.5, 13.5),
    (60, 61, "Sachsen-Anhalt: Tiefland", 52.0, 11.8),
    (60, 62, "Sachsen-Anhalt: Harz", 51.7, 10.8),
    (70, 71, "Thüringen: Tiefland", 51.0, 11.0),
    (70, 72, "Thüringen: Mittelgebirge", 50.7, 10.5),
    (80, 81, "Sachsen: Tiefland", 51.3, 13.5),
    (80, 82, "Sachsen: Mittelgebirge", 50.8, 13.0),
    (90, 91, "Hessen: Nordhessen/Mittelgebirge", 51.0, 9.5),
    (90, 92, "Hessen: Rhein-Main", 50.1, 8.7),
    (100, 101, "Rheinland-Pfalz: Rhein/Pfalz/Nahe/Mosel", 49.8, 7.5),
    (100, 102, "Rheinland-Pfalz: Mittelgebirge", 50.3, 7.0),
    (100, 103, "Saarland", 49.4, 7.0),
    (110, 111, "Baden-Württemberg: Oberrhein/unt. Neckartal", 49.0, 8.5),
    (110, 112, "Baden-Württemberg: Hohenlohe/mittl. Neckar/Oberschwaben", 48.8, 9.5),
    (110, 113, "Baden-Württemberg: Mittelgebirge", 48.3, 8.2),
    (120, 121, "Bayern: Allgäu/Oberbayern/Bay. Wald", 48.0, 12.0),
    (120, 122, "Bayern: Donauniederungen", 48.8, 12.5),
    (120, 123, "Bayern: nördl. Donau (ohne Bay. Wald/Mainfranken)", 49.2, 11.5),
    (120, 124, "Bayern: Mainfranken", 49.8, 10.0),
]


def _entfernung(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Entfernung zweier Koordinaten in km (Haversine)."""
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _naechste_region(lat: float, lon: float) -> tuple[int, int, str, float]:
    beste: tuple[int, int, str, float] = (*REGIONEN[0][:3], float("inf"))
    for region_id, partregion_id, name, rlat, rlon in REGIONEN:
        d = _entfernung(lat, lon, rlat, rlon)
        if d < beste[3]:
            beste = (region_id, partregion_id, name, d)
    return beste


def _stufe(rohwert: str) -> dict:
    info = STUFEN.get(rohwert, STUFEN["-1"])
    return {"raw": rohwert, "value": info["value"], "label": info["label"], "color": info["color"]}


def _leer(region_name: str) -> dict:
    leer = _stufe("-1")
    arten = {
        SCHLUESSEL[key]: {
            "name": ARTEN[key],
            "icon": EMOJIS[key],
            "today": leer,
            "tomorrow": leer,
            "dayafter": leer,
        }
        for key in ARTEN
    }
    return {
        "region": {"id": -1, "partregion_id": -1, "name": region_name, "partregion_name": ""},
        "last_update": "",
        "next_update": "",
        "max_level_today": -1,
        "arten": arten,
    }


async def hole(lat: float, lon: float) -> dict | None:
    """Pollenflug-Daten fuer Koordinaten (naechste DWD-Region).

    Der DWD-Gefahrenindex deckt nur Deutschland ab; fuer weit entfernte Orte
    gibt es keine Pollendaten (None statt einer unpassenden Ersatzregion).
    """
    region_id, partregion_id, region_name, distanz = _naechste_region(lat, lon)
    if distanz > 250:
        return None

    async with httpx.AsyncClient(timeout=30, trust_env=False, headers={"User-Agent": "Wetterwarte/1.0"}) as client:
        antwort = await client.get(DWD_POLLEN_URL)
        antwort.raise_for_status()
        daten = antwort.json()

    region_daten = None
    for eintrag in daten.get("content", []):
        if eintrag.get("region_id") == region_id and eintrag.get("partregion_id") == partregion_id:
            region_daten = eintrag
            break
    if region_daten is None:
        for eintrag in daten.get("content", []):
            if eintrag.get("region_id") == region_id:
                region_daten = eintrag
                break
    if region_daten is None:
        return _leer(region_name)

    roh = region_daten.get("Pollen", {})
    arten = {}
    for key in ARTEN:
        werte = roh.get(key, {})
        arten[SCHLUESSEL[key]] = {
            "name": ARTEN[key],
            "icon": EMOJIS[key],
            "today": _stufe(werte.get("today", "-1")),
            "tomorrow": _stufe(werte.get("tomorrow", "-1")),
            "dayafter": _stufe(werte.get("dayafter_to", "-1")),
        }

    max_heute = max((a["today"]["value"] for a in arten.values() if a["today"]["value"] >= 0), default=0)

    return {
        "region": {
            "id": region_id,
            "partregion_id": partregion_id,
            "name": region_daten.get("region_name", region_name),
            "partregion_name": region_daten.get("partregion_name", ""),
        },
        "last_update": daten.get("last_update", ""),
        "next_update": daten.get("next_update", ""),
        "max_level_today": max_heute,
        "arten": arten,
    }
