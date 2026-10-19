"""Lage am Ort aus Radar, Modell, Warnungen und Blitzen (lage.py, Regeln in docs/WARNUNGEN.md)."""

from datetime import UTC, datetime, timedelta

from wetterwarte import ansagen, lage
from wetterwarte.zeit import zone

TZ = "Europe/Berlin"
JETZT = datetime(2026, 10, 19, 16, 0, tzinfo=UTC)  # 18:00 Ortszeit


def _basis(regen_h=None, codes=None, boeen=None, viertel=None) -> dict:
    """Modell ab der laufenden Stunde (Ortszeit ohne Versatz wie Open-Meteo), 13 Stunden."""
    start = JETZT.astimezone(zone(TZ)).replace(tzinfo=None)
    zeiten = [(start + timedelta(hours=i)).isoformat(timespec="minutes") for i in range(13)]
    basis = {"hourly": {
        "time": zeiten,
        "precipitation": regen_h or [0.0] * 13,
        "weather_code": codes or [3] * 13,
        "wind_gusts_10m": boeen or [20.0] * 13,
    }}
    if viertel is not None:
        basis["minutely_15"] = {
            "time": [(start + timedelta(minutes=15 * i)).isoformat(timespec="minutes") for i in range(len(viertel))],
            "precipitation": viertel,
        }
    return basis


def _radar(werte: list[float | None], basis: datetime = JETZT) -> dict:
    return {"basis": basis.isoformat(), "versatz_min": [5 * i for i in range(len(werte))], "werte": werte}


def _art(ereignisse, art):
    return [e for e in ereignisse if e.art == art]


def test_leichter_regen_aus_dem_radar_in_25_minuten():
    radar = _radar([0.0] * 5 + [0.8] * 6 + [0.0] * 14)
    (e,) = _art(lage.ermittle(_basis(), radar, [], None, TZ, JETZT), "niederschlag")
    assert (e.klasse, e.quelle, e.vorlauf_min, e.vorlaufstufe, e.laeuft) == ("regen_leicht", "radar", 25, 30, False)
    assert e.bausteine == ["regen_leicht_30"]
    assert e.text == "Es wird in deiner Region in 30 Minuten leicht regnen."
    assert e.titel == "Leichter Regen in 30 Minuten"


def test_radar_geht_vor_dem_modell():
    # Das Modell sieht Regen in einer halben Stunde, das Radar bleibt zwei Stunden trocken: es zählt das Radar.
    basis = _basis(viertel=[0, 0, 0.8, 0.8, 0.8, 0.8] + [0] * 10)
    assert not _art(lage.ermittle(basis, _radar([0.0] * 25), [], None, TZ, JETZT), "niederschlag")
    (e,) = _art(lage.ermittle(basis, None, [], None, TZ, JETZT), "niederschlag")
    assert e.quelle == "vorhersage" and e.vorlauf_min == 30 and e.klasse == "regen"


def test_regnet_schon_laeuft_und_kuendigt_nichts_an():
    (e,) = _art(lage.ermittle(_basis(), _radar([1.5] * 25), [], None, TZ, JETZT), "niederschlag")
    assert e.laeuft and e.bausteine == [] and e.vorlaufstufe is None


def test_einzelner_radarpunkt_ist_keine_episode():
    radar = _radar([0.0] * 4 + [3.0] + [0.0] * 20)
    assert not _art(lage.ermittle(_basis(), radar, [], None, TZ, JETZT), "niederschlag")


def test_schnee_in_drei_stunden_aus_den_stunden():
    regen = [0.0] * 3 + [1.0, 1.0] + [0.0] * 8
    codes = [3] * 3 + [73, 73] + [3] * 8
    (e,) = _art(lage.ermittle(_basis(regen_h=regen, codes=codes), _radar([0.0] * 25), [], None, TZ, JETZT), "niederschlag")
    assert (e.klasse, e.vorlauf_min, e.vorlaufstufe) == ("schnee", 180, 180)
    assert e.text == "Es wird in deiner Region in 3 Stunden schneien."


def test_gefrierender_regen_ist_stufe_3_mit_achtung():
    regen = [0.0, 0.5] + [0.0] * 11
    codes = [3, 66] + [3] * 11
    (e,) = _art(lage.ermittle(_basis(regen_h=regen, codes=codes), None, [], None, TZ, JETZT), "niederschlag")
    assert e.klasse == "glatteis" and e.stufe == 3 and e.bausteine[0] == "achtung"


def test_sturm_kuendigt_die_staerkste_klasse_mit_spitzenboee_an():
    boeen = [20, 30, 70, 80, 96, 60] + [20] * 7
    (e,) = _art(lage.ermittle(_basis(boeen=boeen), None, [], None, TZ, JETZT), "wind")
    assert e.klasse == "schwere_sturmboeen" and e.stufe == 3 and e.vorlauf_min == 240
    assert e.bausteine == ["achtung", "schwere_sturmboeen_240", "boeen_95"]


def test_gewitter_mit_hagel_aus_dem_wettercode():
    codes = [3, 3, 95, 96, 3] + [3] * 8
    (e,) = _art(lage.ermittle(_basis(codes=codes), None, [], None, TZ, JETZT), "gewitter")
    assert e.klasse == "gewitter_hagel" and e.vorlauf_min == 120 and e.vorlaufstufe == 180


def test_blitze_in_der_naehe():
    ms = JETZT.timestamp() * 1000
    roh = {"einschlaege": [{"km": 8.2, "grad": 90, "zeit": ms - 5 * 60_000}, {"km": 3.0, "grad": 90, "zeit": ms - 40 * 60_000}]}
    (e,) = [x for x in lage.ermittle(None, None, [], roh, TZ, JETZT) if x.schluessel == "blitze"]
    assert e.art == "gewitter" and e.rang == 2 and e.bausteine == ["blitze_10"]
    assert e.text == "Ein Gewitter ist etwa 10 Kilometer entfernt."


def test_amtliche_warnung_fuer_morgen():
    w = {"stufe": 3, "ereignis": "Schwere Sturmböen", "von": "2026-10-20T06:00:00+02:00", "bis": "2026-10-20T18:00:00+02:00"}
    (e,) = lage.ermittle(None, None, [w], None, TZ, JETZT)
    assert e.bausteine == ["warnung_3", "dwd_schwere_sturmboeen", "ab_morgen_6", "bis_morgen_18"]
    assert e.text == "Amtliche Unwetterwarnung für deine Region. Schwere Sturmböen. Ab morgen 6 Uhr. Bis morgen 18 Uhr."
    assert e.vorlaufstufe is None


def test_unbekanntes_ereignis_verweist_auf_die_einzelheiten():
    w = {"stufe": 1, "ereignis": "Unbekanntes Wetter", "von": None, "bis": "2026-10-19T21:00:00+02:00"}
    (e,) = lage.ermittle(None, None, [w], None, TZ, JETZT)
    assert e.bausteine == ["warnung_1", "warnung_einzelheiten", "ab_sofort", "bis_21"]


def test_jeder_baustein_steht_im_katalog():
    radar = _radar([0.0] * 5 + [30.0] * 6 + [0.0] * 14)
    w = {"stufe": 4, "ereignis": "Orkanböen", "von": None, "bis": None}
    ereignisse = lage.ermittle(_basis(boeen=[130] * 13, codes=[99] * 13), radar, [w], None, TZ, JETZT)
    assert {e.art for e in ereignisse} == {"warnung", "niederschlag", "gewitter", "wind"}
    for e in ereignisse:
        assert all(b in ansagen.alle() for b in e.bausteine), e
    assert ereignisse[0].stufe == 4  # höchste Stufe zuerst
