"""Buchführung der Meldungen (melden.py): neu, dringlicher, stärker, still neu scharf, Entwarnung, Nachtruhe,
Ausfall einer Quelle."""

from datetime import UTC, datetime, timedelta

from wetterwarte import melden
from wetterwarte.schemas.geraete import Meldeeinstellungen, Nachtruhe
from wetterwarte.schemas.lage import Ereignis

JETZT = datetime(2026, 10, 19, 16, 0, tzinfo=UTC)
EINST = Meldeeinstellungen(orte=["koeln"])


def _regen(vorlauf: int | None, rang: int = 0, laeuft: bool = False, klasse: str = "regen_leicht", quelle="radar") -> Ereignis:
    stufen = [360, 180, 120, 60, 30, 15]
    stufe_v = min((s for s in stufen if vorlauf is not None and vorlauf <= s), default=None)
    return Ereignis(art="niederschlag", schluessel="niederschlag", klasse=klasse, rang=rang, stufe=1,
                    beginn=JETZT + timedelta(minutes=vorlauf or 0), laeuft=laeuft,
                    vorlauf_min=None if laeuft else vorlauf, vorlaufstufe=None if laeuft else stufe_v,
                    quelle=quelle, titel="Regen", text="Es wird regnen.", bausteine=[] if laeuft else ["regen_leicht_30"])


def _lauf(folge, einst=EINST, **kw):
    """Mehrere Takte nacheinander; je Takt die Zahl der Meldungen."""
    gedaechtnis, anzahlen = {}, []
    for lage in folge:
        meldungen, gedaechtnis = melden.pruefe(lage, gedaechtnis, einst, JETZT, **kw)
        anzahlen.append(len(meldungen))
    return anzahlen, gedaechtnis


def test_regen_wird_gestaffelt_angekuendigt():
    # erst ab dem Vorlauf des Geräts (3 Stunden), dann bei jeder dringlicheren Stufe, gleiche Stufe nur einmal
    anzahlen, _ = _lauf([[_regen(300)], [_regen(170)], [_regen(160)], [_regen(110)], [_regen(55)], [_regen(28)], [_regen(14)], [_regen(9)]])
    assert anzahlen == [0, 1, 0, 1, 1, 1, 1, 0]


def test_staerker_wird_erneut_gemeldet_schwaecher_nicht():
    anzahlen, _ = _lauf([[_regen(50)], [_regen(45, rang=2, klasse="regen_stark")], [_regen(40, rang=0)]])
    assert anzahlen == [1, 1, 0]


def test_spaeterer_beginn_macht_still_neu_scharf():
    # 30 Minuten gemeldet, dann rückt der Regen auf zwei Stunden: still; beim Näherkommen wieder
    anzahlen, _ = _lauf([[_regen(25)], [_regen(110)], [_regen(55)]])
    assert anzahlen == [1, 0, 1]


def test_entwarnung_wenn_angekuendigter_regen_ausbleibt():
    _, gedaechtnis = melden.pruefe([_regen(50)], {}, EINST, JETZT)
    meldungen, gedaechtnis = melden.pruefe([], gedaechtnis, EINST, JETZT)
    assert len(meldungen) == 1 and meldungen[0].entwarnung
    assert meldungen[0].text == "Entwarnung. Der angekündigte Regen bleibt aus."
    assert gedaechtnis == {}


def test_eingetretener_regen_ist_keine_entwarnung_und_danach_neu():
    anzahlen, _ = _lauf([[_regen(20)], [_regen(None, laeuft=True)], [], [_regen(50)]])
    assert anzahlen == [1, 0, 0, 1]


def test_ausfall_der_quelle_entwarnt_nicht_und_meldet_danach_nicht_erneut():
    _, gedaechtnis = melden.pruefe([_regen(50)], {}, EINST, JETZT)
    meldungen, gedaechtnis = melden.pruefe([], gedaechtnis, EINST, JETZT, ausgefallen=frozenset({"radar"}))
    assert meldungen == [] and "niederschlag" in gedaechtnis
    meldungen, _ = melden.pruefe([_regen(48)], gedaechtnis, EINST, JETZT)
    assert meldungen == []


def test_einstellungen_filtern_art_staerke_und_vorlauf():
    nur_stark = Meldeeinstellungen(niederschlag_ab=2)
    assert melden.pruefe([_regen(50)], {}, nur_stark, JETZT)[0] == []
    ohne_regen = Meldeeinstellungen(arten=["warnung", "wind"])
    assert melden.pruefe([_regen(50)], {}, ohne_regen, JETZT)[0] == []
    eine_stunde = Meldeeinstellungen(vorlauf_min=60)
    assert melden.pruefe([_regen(100)], {}, eine_stunde, JETZT)[0] == []
    assert len(melden.pruefe([_regen(55)], {}, eine_stunde, JETZT)[0]) == 1


def test_nachtruhe_laesst_nur_stufe_3_durch_und_vergisst_nichts():
    einst = Meldeeinstellungen(nachtruhe=Nachtruhe(an=True, von=22, bis=7, ab_stufe=3))
    assert melden.in_ruhe(einst, 23) and melden.in_ruhe(einst, 3) and not melden.in_ruhe(einst, 7)
    ruhig = lambda m: m.stufe >= 3  # noqa: E731
    meldungen, gedaechtnis = melden.pruefe([_regen(50)], {}, einst, JETZT, zulassen=ruhig)
    assert meldungen == [] and gedaechtnis == {}
    # am Morgen kommt der dann aktuelle Stand
    assert len(melden.pruefe([_regen(25)], gedaechtnis, einst, JETZT)[0]) == 1


def test_wind_jenseits_der_groessten_stufe_wartet():
    wind = Ereignis(art="wind", schluessel="wind", klasse="sturmboeen", rang=1, stufe=2, beginn=JETZT + timedelta(hours=10),
                    vorlauf_min=600, vorlaufstufe=None, quelle="vorhersage", titel="Sturmböen", text="", bausteine=[])
    assert melden.pruefe([wind], {}, Meldeeinstellungen(vorlauf_min=360), JETZT)[0] == []


def test_blitze_ohne_vorlauf_sofort_und_naeher_erneut():
    def blitz(rang: int) -> Ereignis:
        return Ereignis(art="gewitter", schluessel="blitze", klasse=f"blitze_{rang}", rang=rang, stufe=1, beginn=None,
                        quelle="blitze", titel="Gewitter", text="", bausteine=["blitze_20"])
    anzahlen, _ = _lauf([[blitz(0)], [blitz(0)], [blitz(2)], []])
    assert anzahlen == [1, 0, 1, 0]
