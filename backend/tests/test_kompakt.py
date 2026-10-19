"""Telefon-Antwort aus einer echten Open-Meteo-Antwort (tests/daten) und Beispielbereichen."""

import json
from datetime import UTC, datetime
from pathlib import Path

from wetterwarte import kompakt
from wetterwarte.bereiche import Ergebnis
from wetterwarte.models.ort import Ort

DATEN = Path(__file__).parent / "daten"
JETZT = datetime(2026, 10, 19, 18, 0, tzinfo=UTC)


def _ort() -> Ort:
    return Ort(slug="koeln", name="Köln", region="Nordrhein-Westfalen", land="Deutschland", lat=50.94, lon=6.96, zeitzone="Europe/Berlin")


def _ok(wert):
    return Ergebnis(wert, "ok", JETZT)


def _fehlt():
    return Ergebnis(None, "fehlt", None)


def test_baue_aus_echter_antwort():
    roh = json.loads((DATEN / "openmeteo_koeln.json").read_text())
    k = kompakt.baue(_ort(), _ok(roh), _ok([]), _fehlt(), _fehlt(), _fehlt())
    assert k.jetzt is not None
    assert k.jetzt.zeit.utcoffset() is not None  # Zeiten mit Versatz
    assert str(k.jetzt.zeit.tzinfo) == "Europe/Berlin"
    # laufende Stunde liegt an jetzt_index, davor höchstens 6 Stunden
    laufend = k.stunden[k.jetzt_index].zeit
    assert laufend <= k.jetzt.zeit < laufend.replace(minute=59, second=59)
    assert k.jetzt_index <= kompakt.ZURUECK_H
    assert len(k.stunden) - k.jetzt_index - 1 <= kompakt.VORAUS_H
    assert len(k.tage) == 7 and k.tage[0].sonnenaufgang is not None
    assert k.regen is not None and len(k.regen.werte) == kompakt.REGEN_SCHRITTE
    # Ausfall bleibt sichtbar: fehlende Bereiche sind null mit Status fehlt, Warnungen leer heißt "keine"
    assert k.warnungen == [] and k.bereiche["warnungen"].status == "ok"
    assert k.blitze is None and k.bereiche["blitze"].status == "fehlt"


def test_warnquelle_fehlt_ist_nicht_keine_warnung():
    k = kompakt.baue(_ort(), _fehlt(), _fehlt(), _fehlt(), _fehlt(), _fehlt())
    assert k.warnungen is None
    assert k.bereiche["warnungen"].status == "fehlt"
    assert k.jetzt is None and k.stunden == []


def test_regen_beginn_und_ende():
    roh = {"current": {"time": "2026-10-19T17:20"}, "minutely_15": {
        "time": [f"2026-10-19T{h:02d}:{m:02d}" for h in (17, 18, 19) for m in (0, 15, 30, 45)],
        "precipitation": [0, 0, 0.1, 0.4, 0.5, 0.2, 0, 0, 0, 0, 0, 0],
    }}
    r = kompakt._regen(roh)
    # laufende Viertelstunde ist 17:15 (Index 1): trocken, ab 17:30 nass (0,4 mm/h), ab 18:30 trocken
    assert r.beginn_min == 15 and r.ende_min == 75
    assert r.werte[0] == 0 and r.max_mm_h == 2.0
