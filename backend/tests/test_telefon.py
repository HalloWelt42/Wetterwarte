"""Telefon-Katalog: Vorlage ist gültig, Prüfung weist Fehler mit Grund ab."""

import pytest

from wetterwarte import telefon


def _vorlage():
    return telefon.vorlage().model_copy(deep=True)


def _w(v):
    return v.seiten["wetter"]


def test_vorlage_ist_gueltig_und_hat_eindeutige_ids():
    v = telefon.vorlage()
    telefon.pruefe(v)
    alle = [k.id for s in v.seiten.values() for k in s]
    assert len(set(alle)) == len(alle)
    assert set(v.seiten) == {"wetter", "gesundheit"}
    assert telefon.vorlage().seiten["wetter"][0].id != v.seiten["wetter"][0].id


def test_jede_katalog_groesse_passt_ins_raster():
    for typ, t in telefon.katalog()["typen"].items():
        for g in t["groessen"]:
            w, h = (int(x) for x in g.split("x"))
            assert 1 <= w <= 3 and 1 <= h <= 3, (typ, g)


@pytest.mark.parametrize(
    ("aendern", "grund"),
    [
        (lambda v: setattr(_w(v)[1], "x", 1), "überlappt"),
        (lambda v: setattr(_w(v)[1], "h", 2), "Größe 1x2"),
        (lambda v: setattr(_w(v)[3], "x", 1), "außerhalb"),
        (lambda v: setattr(_w(v)[0], "typ", "uhr"), "Unbekannter Kacheltyp"),
        (lambda v: setattr(_w(v)[2], "id", _w(v)[1].id), "doppelt"),
        (lambda v: setattr(_w(v)[2], "id", v.seiten["gesundheit"][0].id), "doppelt"),
        (lambda v: _w(v)[7].conf.update(groesse="regenbogen"), "nicht vorgesehen"),
        (lambda v: v.seiten["gesundheit"][2].conf.update(allergien=["birke", "kaktus"]), "nicht vorgesehene"),
        (lambda v: _w(v)[0].conf.update(titel="Hallo"), "unbekannte Einstellung"),
        (lambda v: v.seiten["gesundheit"].append(_w(v)[0].model_copy(update={"id": "neu", "y": 20})), "gehört nicht auf die Seite"),
        (lambda v: v.seiten.update(karte=[]), "Unbekannte Seite"),
    ],
)
def test_pruefung_weist_ab(aendern, grund):
    v = _vorlage()
    aendern(v)
    with pytest.raises(ValueError, match=grund):
        telefon.pruefe(v)


@pytest.mark.parametrize("name", ["Zuhause", "Unwetter", "Garten", "Reise", "Irgendwas"])
def test_profilvorlagen_sind_gueltig(name):
    v = telefon.vorlage(name)
    telefon.pruefe(v)
    assert set(v.seiten) == {"wetter", "gesundheit"}


def test_unwetter_hat_eigene_vorlage():
    typen = [k.typ for k in telefon.vorlage("Unwetter").seiten["wetter"]]
    assert "warnungen" in typen and "blitze" in typen
