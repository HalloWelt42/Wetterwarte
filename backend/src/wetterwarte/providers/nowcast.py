"""Regen-Nowcast des Deutschen Wetterdienstes (RADVOR RV) je Ort: Regenrate in mm/h in 5-Minuten-Schritten von
der Analyse bis zwei Stunden voraus.

Ein Archiv (rund 100 KB) bedient alle Orte: beim Auffrischen werden die Reihen aller gespeicherten Orte auf
einmal herausgelesen, ohne die Gitter ganz zu dekodieren (radar.werte_an). Orte außerhalb des Radargebiets
stehen in `ausserhalb`; für sie gilt das Vorhersagemodell."""

import asyncio
import io
import re
import tarfile

import httpx
import numpy as np

from ..config import settings
from . import radar


async def hole(punkte: dict[str, int]) -> dict:
    """Neuestes RV-Archiv holen und die Reihen der Punkte (Slug -> flacher Gitterindex) herauslesen."""
    basis_url = f"{settings.dwd_radar_base}/composite/rv/"
    async with httpx.AsyncClient() as client:
        listing = (await radar._hole(client, basis_url)).decode("latin-1", "replace")
        stempel = sorted(set(re.findall(r"DE1200_RV(\d{10})\.tar\.bz2", listing)))
        if not stempel:
            raise RuntimeError("kein RADVOR-Archiv im Verzeichnis")
        daten = await radar._hole(client, f"{basis_url}DE1200_RV{stempel[-1]}.tar.bz2")
    return await asyncio.to_thread(reihen, daten, stempel[-1], punkte)


def reihen(daten: bytes, stempel: str, punkte: dict[str, int]) -> dict:
    """Je Punkt die Raten aller Vorhersageschritte (None ohne Messwert)."""
    slugs = [s for s, i in punkte.items() if i >= 0]
    indizes = np.array([punkte[s] for s in slugs], dtype=np.int64)
    schritte: dict[int, np.ndarray] = {}
    with tarfile.open(fileobj=io.BytesIO(daten), mode="r|bz2") as tar:
        for m in tar:
            treffer = re.search(r"_(\d{3})$", m.name)
            datei = tar.extractfile(m) if treffer else None
            if datei is not None and treffer is not None:
                schritte[int(treffer.group(1))] = radar.werte_an(datei.read(), indizes)
    versatz = sorted(schritte)
    ergebnis: dict[str, list[float | None]] = {}
    for j, slug in enumerate(slugs):
        werte = [schritte[v][j] for v in versatz]
        if all(np.isnan(w) for w in werte):
            continue  # Radargebiet, aber ohne Messung (Rand, Ausfall): wie außerhalb behandeln
        ergebnis[slug] = [None if np.isnan(w) else round(float(w), 2) for w in werte]
    return {
        "basis": radar._ts(stempel).isoformat(),
        "versatz_min": versatz,
        "reihen": ergebnis,
        "ausserhalb": sorted(s for s in punkte if s not in ergebnis),
    }
