"""Eigenes DWD-RADOLAN-Regenradar: holt die Rohdaten von DWD OpenData, dekodiert
das RADOLAN-Binaerformat, reprojiziert per vorab gebackener Indexkarte nach
Web-Mercator und rendert farbige PNG-Kacheln fuer das Karten-Overlay.

Zwei Produkte, mm/h, eine gemeinsame Bild-Ausgabe (deckungsgleich):
- RY  (radolan/ry):     gemessene Regenrate, 5 min, Gitter 900x900  -> Vergangenheit
- RV  (composite/rv):   RADVOR-Nowcast, Analyse + bis +2 h, DE1200  -> jetzt + Vorhersage

Zur Laufzeit werden nur numpy und pillow gebraucht (keine Geo-Bibliotheken):
die stereographische Reprojektion steckt fertig in den Indexkarten (data/*.npz),
die offline mit wradlib/pyproj erzeugt wurden.
"""

import asyncio
import bz2
import io
import math
import re
import tarfile
from datetime import datetime, timedelta, timezone
from importlib.resources import files

import httpx
import numpy as np
from PIL import Image

from ..config import settings

# --- Indexkarten laden (Reprojektion RADOLAN-Gitter -> gemeinsames Mercator-Raster) ---


def _lade_index(name: str) -> dict:
    with (files("wetterwarte.assets") / name).open("rb") as fh:
        z = np.load(fh)
        return {
            "quelle": z["quelle"].astype(np.int32),
            "coords": [list(map(float, z[k])) for k in ("tl", "tr", "br", "bl")],
        }


_IDX_900 = _lade_index("radar_index_900.npz")
_IDX_1200 = _lade_index("radar_index_de1200.npz")
# Beide Indexkarten teilen dieselbe Ausgabe-Bbox -> eine Bild-Overlay-Koordinate.
COORDS = _IDX_900["coords"]

def punkt_index(lat: float, lon: float) -> int:
    """Flacher Index im DE1200-Gitter (RV) für einen Ort, -1 außerhalb des Radargebiets. Die Indexkarte bildet
    das Mercator-Ausgabebild (Ecken COORDS, linear in Web-Mercator) auf das RADOLAN-Gitter ab."""
    (west, nord), _, (ost, sued), _ = _IDX_1200["coords"]
    q = _IDX_1200["quelle"]
    hoehe, breite = q.shape

    def merc(breitengrad: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(breitengrad) / 2))

    if not (west <= lon < ost and sued < lat <= nord):
        return -1
    spalte = int((lon - west) / (ost - west) * breite)
    zeile = int((merc(nord) - merc(lat)) / (merc(nord) - merc(sued)) * hoehe)
    if not (0 <= zeile < hoehe and 0 <= spalte < breite):
        return -1
    return int(q[zeile, spalte])


# Anzahl gemessener Vergangenheits-Frames (RY, 5-min-Schritte).
RY_ANZAHL = 10

# Farbskala Regenrate (mm/h) -> RGBA. Untergrenze je Stufe.
_STOPS = [
    (0.1, (77, 141, 242, 140)),
    (0.5, (41, 128, 230, 180)),
    (1.0, (38, 199, 184, 205)),
    (2.0, (64, 204, 89, 219)),
    (5.0, (242, 230, 77, 230)),
    (10.0, (250, 158, 51, 237)),
    (20.0, (235, 77, 51, 242)),
    (40.0, (191, 51, 191, 247)),
]


def _kopf(rohbytes: bytes) -> tuple[int, float, float]:
    """Ende des Kopfs, Genauigkeit (PR) und Faktor auf mm/h aus dem Kopf einer RADOLAN-Datei.

    RY und RV liefern die Niederschlagshöhe eines Intervalls (INT, Minuten) in Schritten der Genauigkeit
    (PR E-02 = 0,01 mm); eine Rate in mm/h ist also Höhe mal 60 durch Intervall."""
    etx = rohbytes.find(b"\x03")
    kopf = rohbytes[:etx].decode("latin-1", "replace")
    pr = re.search(r"PR\s*E-(\d\d)", kopf)
    intervall = re.search(r"INT\s*(\d+)", kopf)
    genauigkeit = 10.0 ** -int(pr.group(1)) if pr else 0.01
    minuten = int(intervall.group(1)) if intervall and int(intervall.group(1)) > 0 else 60
    return etx, genauigkeit, 60.0 / minuten


def _decode(rohbytes: bytes, ny: int, nx: int) -> np.ndarray:
    """RADOLAN-Binaer -> Regenrate mm/h (NaN = keine Messung/kein Regenwert)."""
    etx, genauigkeit, je_stunde = _kopf(rohbytes)
    p = np.frombuffer(rohbytes[etx + 1 : etx + 1 + ny * nx * 2], dtype="<u2").reshape(ny, nx)
    wert = (p & 0x0FFF).astype("f4") * (genauigkeit * je_stunde)
    wert[(p & 0x2000) != 0] = np.nan  # No-Data-/Clutter-Kennung
    wert[wert > 2400] = np.nan  # über 200 mm in 5 Minuten ist kein Niederschlag
    return wert


def werte_an(rohbytes: bytes, indizes: np.ndarray) -> np.ndarray:
    """Regenrate (mm/h) an einzelnen Gitterpunkten (flache Indizes, -1 = außerhalb), ohne das ganze Gitter
    zu dekodieren; NaN ohne Messung. Für den Nowcast je Ort."""
    etx, genauigkeit, je_stunde = _kopf(rohbytes)
    roh = np.frombuffer(rohbytes, dtype="u1", offset=etx + 1)
    ergebnis = np.full(indizes.shape, np.nan, dtype="f4")
    gueltig = (indizes >= 0) & (indizes * 2 + 1 < roh.size)
    i = indizes[gueltig]
    p = roh[i * 2].astype(np.uint16) | (roh[i * 2 + 1].astype(np.uint16) << 8)
    wert = (p & 0x0FFF).astype("f4") * (genauigkeit * je_stunde)
    wert[(p & 0x2000) != 0] = np.nan
    wert[wert > 2400] = np.nan
    ergebnis[gueltig] = wert
    return ergebnis


def _render(wert: np.ndarray, idx: dict) -> bytes:
    """Werte per Indexkarte samplen und als farbiges PNG (RGBA) rendern."""
    q = idx["quelle"]
    flach = wert.ravel()
    out = np.full(q.size, np.nan, dtype="f4")
    gueltig = q.ravel() >= 0
    out[gueltig] = flach[q.ravel()[gueltig]]
    out = out.reshape(q.shape)
    rgba = np.zeros((q.shape[0], q.shape[1], 4), dtype="u1")
    for i, (lo, farbe) in enumerate(_STOPS):
        hi = _STOPS[i + 1][0] if i + 1 < len(_STOPS) else 1e12
        maske = (out >= lo) & (out < hi)
        rgba[maske] = farbe
    puffer = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(puffer, format="PNG", optimize=False, compress_level=6)
    return puffer.getvalue()


def _ts(kompakt: str) -> datetime:
    """RADOLAN-Zeitstempel 'YYMMDDHHMM' (UTC) -> datetime."""
    return datetime.strptime(kompakt, "%y%m%d%H%M").replace(tzinfo=timezone.utc)


# --- Zustand (im Speicher): gerenderte Frames + Metadaten ---

_cache: dict[str, bytes] = {}  # frame-id -> PNG
_frames: list[dict] = []  # geordnete Metadaten [{id, zeit, offset, art}]
_stand: datetime | None = None
_lock = asyncio.Lock()
TTL = timedelta(minutes=2)


async def _hole(client: httpx.AsyncClient, url: str) -> bytes:
    r = await client.get(url, timeout=30)
    r.raise_for_status()
    return r.content


async def _ry_frames(client: httpx.AsyncClient) -> list[dict]:
    """Die letzten RY-Frames (gemessen) holen, dekodieren, rendern - mit Cache je Zeit."""
    basis = f"{settings.dwd_radar_base}/radolan/ry/"
    listing = (await _hole(client, basis)).decode("latin-1", "replace")
    namen = re.findall(r"raa01-ry_10000-(\d{10})-dwd---bin\.bz2", listing)
    namen = sorted(set(namen))[-RY_ANZAHL:]
    ergebnis = []
    for kompakt in namen:
        fid = f"ry-{kompakt}"
        if fid not in _cache:
            gepackt = await _hole(client, f"{basis}raa01-ry_10000-{kompakt}-dwd---bin.bz2")
            # Entpacken, Dekodieren und Zeichnen kosten je Bild Hunderte Millisekunden: nicht im Event-Loop.
            _cache[fid] = await asyncio.to_thread(_ry_bild, gepackt)
        ergebnis.append({"id": fid, "zeit": _ts(kompakt), "art": "gemessen"})
    return ergebnis


async def _rv_frames(client: httpx.AsyncClient) -> list[dict]:
    """Aktuelle RV-Nowcast-Frames (Analyse + Vorhersage) aus dem neuesten Archiv."""
    basis = f"{settings.dwd_radar_base}/composite/rv/"
    listing = (await _hole(client, basis)).decode("latin-1", "replace")
    stempel = re.findall(r"DE1200_RV(\d{10})\.tar\.bz2", listing)
    if not stempel:
        return []
    neuest = sorted(set(stempel))[-1]
    daten = await _hole(client, f"{basis}DE1200_RV{neuest}.tar.bz2")
    basiszeit = _ts(neuest)
    stufen = await asyncio.to_thread(_rv_bilder, daten, neuest, set(_cache))
    ergebnis = []
    for fid, (png, offset) in sorted(stufen.items(), key=lambda e: e[1][1]):
        if png is not None:
            _cache[fid] = png
        ergebnis.append({"id": fid, "zeit": basiszeit + timedelta(minutes=offset), "art": "vorhersage"})
    return ergebnis


def _ry_bild(gepackt: bytes) -> bytes:
    return _render(_decode(bz2.decompress(gepackt), 900, 900), _IDX_900)


def _rv_bilder(daten: bytes, neuest: str, vorhanden: set[str]) -> dict[str, tuple[bytes | None, int]]:
    """Alle Vorhersagestufen eines RV-Archivs: je Stufe (Bild oder None, wenn schon vorhanden; Offset)."""
    ergebnis: dict[str, tuple[bytes | None, int]] = {}
    with tarfile.open(fileobj=io.BytesIO(daten), mode="r:bz2") as tar:
        for m in tar.getmembers():
            treffer = re.search(r"_(\d{3})$", m.name)
            if not treffer:
                continue
            offset = int(treffer.group(1))
            if offset == 0:
                continue  # 0 min deckt bereits der gemessene RY-Strang ab
            fid = f"rv-{neuest}-{offset:03d}"
            png = None if fid in vorhanden else _render(_decode(tar.extractfile(m).read(), 1200, 1100), _IDX_1200)
            ergebnis[fid] = (png, offset)
    return ergebnis


async def aktualisiere(force: bool = False) -> None:
    """Frames auffrischen (Single-Flight, TTL). Fehler lassen den alten Stand stehen."""
    global _stand, _frames
    jetzt = datetime.now(timezone.utc)
    if not force and _stand is not None and (jetzt - _stand) < TTL:
        return
    async with _lock:
        if not force and _stand is not None and (datetime.now(timezone.utc) - _stand) < TTL:
            return
        async with httpx.AsyncClient() as client:
            gemessen = await _ry_frames(client)
            try:
                vorhersage = await _rv_frames(client)
            except Exception:
                vorhersage = []
        neu = gemessen + vorhersage
        if not neu:
            return
        # Bezugszeit "jetzt" = neuester gemessener Frame; Offsets in Minuten dazu.
        bezug = max((f["zeit"] for f in gemessen), default=neu[-1]["zeit"])
        for f in neu:
            f["offset"] = round((f["zeit"] - bezug).total_seconds() / 60)
        # Karenz-Puffer: Frames NICHT sofort entsorgen, sobald ein neues Archiv kommt -
        # sonst laufen kurz noch referenzierte IDs (zweite Karte, Auffrisch-Fenster) ins
        # Leere. Zeitbasiert behalten: Vorhersage 15 min, gemessen 75 min.
        jetzt2 = datetime.now(timezone.utc)

        def _zu_alt(fid: str, minuten: int) -> bool:
            try:
                return _ts(fid.split("-")[1]) < jetzt2 - timedelta(minutes=minuten)
            except Exception:
                return False

        for k in list(_cache.keys()):
            if k.startswith("rv-") and _zu_alt(k, 15):
                _cache.pop(k, None)
            elif k.startswith("ry-") and _zu_alt(k, 75):
                _cache.pop(k, None)
        _frames = neu
        _stand = datetime.now(timezone.utc)


def rahmen() -> dict:
    """Aktuelle Frame-Liste + gemeinsame Bild-Eckkoordinaten (fuer die Karte)."""
    return {
        "coords": COORDS,
        "stand": _stand.isoformat() if _stand else None,
        "frames": [
            {"id": f["id"], "zeit": f["zeit"].isoformat(), "offset": f["offset"], "art": f["art"]}
            for f in _frames
        ],
    }


def bild(fid: str) -> bytes | None:
    return _cache.get(fid)
