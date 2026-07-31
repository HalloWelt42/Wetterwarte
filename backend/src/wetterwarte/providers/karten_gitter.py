"""Flaechen-Overlays fuer die grosse Karte aus einem Open-Meteo-Gitter ueber
Deutschland: Temperatur als interpoliertes Farbfeld (PNG) und Wind als
Pfeil-Punkte (GeoJSON). Ein Abruf speist beide; kurz gecacht.
"""

import asyncio
import io
import json
from datetime import datetime, timedelta, timezone
from importlib.resources import files

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..config import settings

# Gitter ueber Deutschland (Bbox). Punkte = Zellmittelpunkte, Ecken = Bbox-Ecken.
LON0, LON1, LAT0, LAT1 = 5.8, 15.1, 47.2, 55.1
NLON, NLAT = 16, 12
_LONS = np.linspace(LON0, LON1, NLON)
_LATS = np.linspace(LAT0, LAT1, NLAT)  # aufsteigend: Sued -> Nord
# Bild-Eckkoordinaten fuer die MapLibre image-source (oben = Nord).
COORDS = [[LON0, LAT1], [LON1, LAT1], [LON1, LAT0], [LON0, LAT0]]

TTL = timedelta(minutes=10)
_cache: dict = {"grid": None, "stand": None}
_lock = asyncio.Lock()

# Temperatur-Farbskala (RdYlBu umgekehrt), Anker in Grad C -> RGB.
_T_XS = [-10, -5, 0, 5, 10, 15, 18, 22, 26, 30, 35, 40]
_T_R = [49, 69, 116, 171, 224, 255, 255, 254, 253, 244, 215, 165]
_T_G = [54, 117, 173, 217, 243, 255, 255, 224, 174, 109, 48, 0]
_T_B = [149, 180, 209, 233, 248, 191, 191, 144, 97, 67, 39, 38]


async def _hole_grid() -> dict:
    """Gitterwerte (Temperatur + Wind) von Open-Meteo holen, gecacht."""
    jetzt = datetime.now(timezone.utc)
    if _cache["grid"] is not None and _cache["stand"] and (jetzt - _cache["stand"]) < TTL:
        return _cache["grid"]
    async with _lock:
        if _cache["grid"] is not None and _cache["stand"] and (datetime.now(timezone.utc) - _cache["stand"]) < TTL:
            return _cache["grid"]
        punkte = [(la, lo) for la in _LATS for lo in _LONS]
        la = ",".join(f"{p[0]:.3f}" for p in punkte)
        lo = ",".join(f"{p[1]:.3f}" for p in punkte)
        url = (
            f"{settings.open_meteo_base}/forecast?latitude={la}&longitude={lo}"
            "&current=temperature_2m,wind_speed_10m,wind_direction_10m&wind_speed_unit=kmh&timezone=UTC"
        )
        async with httpx.AsyncClient(timeout=30) as client:
            antwort = await client.get(url)
            antwort.raise_for_status()
            daten = antwort.json()
        reihen = daten if isinstance(daten, list) else [daten]
        temp = np.array([r["current"]["temperature_2m"] for r in reihen], dtype="f4").reshape(NLAT, NLON)
        tempo = np.array([r["current"]["wind_speed_10m"] for r in reihen], dtype="f4").reshape(NLAT, NLON)
        richtung = np.array([r["current"]["wind_direction_10m"] for r in reihen], dtype="f4").reshape(NLAT, NLON)
        _cache["grid"] = {"temp": temp, "tempo": tempo, "richtung": richtung}
        _cache["stand"] = datetime.now(timezone.utc)
        return _cache["grid"]


# --- Deutschland-Maske (Temperatur-Feld nur ueber Deutschland, weiche Kante) ---
_GRENZE: list | None = None
_MASKE: dict = {}


def _grenz_ringe() -> list:
    global _GRENZE
    if _GRENZE is None:
        with (files("wetterwarte.assets") / "deutschland_grenze.json").open("rb") as fh:
            _GRENZE = json.load(fh)["ringe"]
    return _GRENZE


def _punkt_in_ring(lon: float, lat: float, ring: list) -> bool:
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


_GRID_DE: np.ndarray | None = None


def _grid_in_deutschland() -> np.ndarray:
    """Bool-Gitter (NLAT x NLON): liegt der Gitterpunkt in Deutschland? (einmal berechnet)."""
    global _GRID_DE
    if _GRID_DE is None:
        ringe = _grenz_ringe()
        m = np.zeros((NLAT, NLON), dtype=bool)
        for i, la in enumerate(_LATS):
            for j, lo in enumerate(_LONS):
                m[i, j] = any(_punkt_in_ring(float(lo), float(la), r) for r in ringe)
        _GRID_DE = m
    return _GRID_DE


def _deutschland_maske(hoehe: int, breite: int) -> np.ndarray:
    """Weiche Alpha-Maske (0..1): 1 innerhalb Deutschlands, 0 ausserhalb."""
    key = (hoehe, breite)
    if key in _MASKE:
        return _MASKE[key]
    img = Image.new("L", (breite, hoehe), 0)
    zeichner = ImageDraw.Draw(img)
    for ring in _grenz_ringe():
        pts = [((lo - LON0) / (LON1 - LON0) * breite, (LAT1 - la) / (LAT1 - LAT0) * hoehe) for lo, la in ring]
        zeichner.polygon(pts, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(1.0))  # weiche Grenzkante
    maske = np.asarray(img, dtype="f4") / 255.0
    _MASKE[key] = maske
    return maske


def _upsample(a: np.ndarray, hoehe: int, breite: int) -> np.ndarray:
    """Regelmaessiges Gitter bilinear auf (hoehe, breite) hochrechnen."""
    r, c = a.shape
    xs, xt = np.linspace(0, 1, c), np.linspace(0, 1, breite)
    a1 = np.vstack([np.interp(xt, xs, a[i]) for i in range(r)])  # (r, breite)
    ys, yt = np.linspace(0, 1, r), np.linspace(0, 1, hoehe)
    return np.vstack([np.interp(yt, ys, a1[:, j]) for j in range(breite)]).T  # (hoehe, breite)


async def temperatur_png() -> bytes:
    """Temperatur als glattes Farbfeld (halbtransparentes PNG, Nord oben)."""
    grid = await _hole_grid()
    feld = grid["temp"][::-1]  # Zeile 0 = Nord
    H, W = 180, 240
    fein = _upsample(feld, H, W)
    r = np.interp(fein, _T_XS, _T_R).astype("u1")
    g = np.interp(fein, _T_XS, _T_G).astype("u1")
    b = np.interp(fein, _T_XS, _T_B).astype("u1")
    # Alpha nur ueber Deutschland (weiche Kante), sonst durchsichtig.
    a = (_deutschland_maske(H, W) * 150).astype("u1")
    rgba = np.dstack([r, g, b, a])
    puffer = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(puffer, format="PNG")
    return puffer.getvalue()


async def wind_geojson() -> dict:
    """Wind-Gitter als GeoJSON-Punkte: Tempo (km/h), Richtung (Grad), Stufe 0-4."""
    grid = await _hole_grid()
    tempo, richtung = grid["tempo"], grid["richtung"]
    in_de = _grid_in_deutschland()
    features = []
    for i, la in enumerate(_LATS):
        for j, lo in enumerate(_LONS):
            if not in_de[i, j]:
                continue  # Wind-Pfeile nur ueber Deutschland zeigen
            v = float(tempo[i, j])
            stufe = 0 if v < 5 else 1 if v < 15 else 2 if v < 30 else 3 if v < 50 else 4
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [float(lo), float(la)]},
                    "properties": {"tempo": round(v), "richtung": round(float(richtung[i, j])), "stufe": stufe},
                }
            )
    return {"type": "FeatureCollection", "features": features}


async def kartendaten() -> dict:
    """Bild-Ecken + Wind-GeoJSON + Temperatur-Rohgitter (fuer Maus-Hover)."""
    grid = await _hole_grid()
    return {
        "coords": COORDS,
        "wind": await wind_geojson(),
        "temp": {
            "lons": [round(float(x), 3) for x in _LONS],
            "lats": [round(float(y), 3) for y in _LATS],
            "werte": [[round(float(v), 1) for v in reihe] for reihe in grid["temp"]],
        },
    }
