"""Satzkatalog der Ansagen (ansagen.py, gemeinsam/meldungen.json)."""

import re

from wetterwarte import ansagen


def test_schluessel_passen_in_den_medienpool():
    for schluessel in ansagen.alle():
        assert re.fullmatch(r"[a-z0-9_-]{1,60}", schluessel), schluessel


def test_sprechform_ohne_ziffern_und_ohne_sonderzeichen():
    for satz in ansagen.alle().values():
        assert not re.search(r"\d", satz.sprechtext), satz
        assert not re.search("[–—“”„‘’]", satz.text), satz


def test_zahlwoerter():
    assert [ansagen.zahlwort(n) for n in (0, 1, 21, 95, 100, 121, 200)] == [
        "null", "eins", "einundzwanzig", "fünfundneunzig", "hundert", "hunderteinundzwanzig", "zweihundert"
    ]
    assert ansagen.sprechform("Ab 1 Uhr.") == "Ab ein Uhr."


def test_zeiten_runden_auf_die_naechste_angabe():
    assert [ansagen.zeit(m)["min"] for m in (3, 12, 25, 100, 140, 200, 330)] == [5, 15, 30, 90, 150, 180, 300]


def test_lange_ereignisse_bekommen_eindeutige_kurze_schluessel():
    lang = "Schweres Gewitter mit extremen Orkanböen, heftigem Starkregen und Hagel"
    assert ansagen.dwd(lang) in ansagen.alle() and len(ansagen.dwd(lang)) <= 60
    assert ansagen.dwd("Sturmböen") == "dwd_sturmboeen"
