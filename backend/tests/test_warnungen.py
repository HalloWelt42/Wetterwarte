"""Warnzeiten in der Zeitzone des Orts."""

from wetterwarte.providers import warnungen


def test_zeitraum_in_ortszeit_aus_utc():
    # 15:00 bis 19:00 UTC sind im Oktober 17:00 bis 21:00 Uhr in Berlin
    text = warnungen.zeitraum("2030-10-19T15:00:00+00:00", "2030-10-19T19:00:00+00:00", "Europe/Berlin")
    assert text == "19.10. 17:00 - 21:00 Uhr"


def test_zeitraum_ueber_mitternacht():
    text = warnungen.zeitraum("2030-10-19T20:00:00+02:00", "2030-10-20T06:00:00+02:00", "Europe/Berlin")
    assert text == "ab 19.10. 20:00 bis 20.10. 06:00"


def test_schreibweise_aus_grossbuchstaben():
    assert warnungen.schreibweise("STARKES GEWITTER") == "Starkes Gewitter"
    assert warnungen.schreibweise("GEWITTER MIT STARKREGEN UND HAGEL") == "Gewitter mit Starkregen und Hagel"
    assert warnungen.schreibweise("Frost") == "Frost"
    assert warnungen.schreibweise("GLÄTTE") == "Glätte"
