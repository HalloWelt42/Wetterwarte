"""Telefon-Katalog: Vorlage ist gültig, Prüfung weist Fehler mit Grund ab."""

import pytest

from wetterwarte import telefon


def _vorlage():
    return telefon.vorlage().model_copy(deep=True)


def test_vorlage_ist_gueltig_und_hat_eindeutige_ids():
    v = telefon.vorlage()
    telefon.pruefe(v)
    assert len({k.id for k in v.kacheln}) == len(v.kacheln)
    assert telefon.vorlage().kacheln[0].id != v.kacheln[0].id


def test_jede_katalog_groesse_passt_ins_raster():
    for typ, t in telefon.katalog()["typen"].items():
        for g in t["groessen"]:
            w, h = (int(x) for x in g.split("x"))
            assert 1 <= w <= 3 and 1 <= h <= 3, (typ, g)


@pytest.mark.parametrize(
    ("aendern", "grund"),
    [
        (lambda v: setattr(v.kacheln[1], "x", 1), "überlappt"),
        (lambda v: setattr(v.kacheln[1], "h", 2), "Größe 1x2"),
        (lambda v: setattr(v.kacheln[3], "x", 1), "außerhalb"),
        (lambda v: setattr(v.kacheln[0], "typ", "uhr"), "Unbekannter Kacheltyp"),
        (lambda v: setattr(v.kacheln[2], "id", v.kacheln[1].id), "doppelt"),
        (lambda v: v.kacheln[10].conf.update(groesse="regenbogen"), "nicht vorgesehen"),
        (lambda v: v.kacheln[7].conf.update(allergien=["birke", "kaktus"]), "nicht vorgesehene"),
        (lambda v: v.kacheln[0].conf.update(titel="Hallo"), "unbekannte Einstellung"),
    ],
)
def test_pruefung_weist_ab(aendern, grund):
    v = _vorlage()
    aendern(v)
    with pytest.raises(ValueError, match=grund):
        telefon.pruefe(v)
