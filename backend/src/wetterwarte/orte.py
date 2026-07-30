"""Beispiel-Orte fuer die Entwicklung.

Nur generische Demo-Daten. Im Betrieb waehlt der Nutzer seine Orte selbst per
Suche; die Ablage erfolgt dann in der Datenbank, nicht im Quellcode.
"""

ORTE: dict[str, dict] = {
    "berlin": {"name": "Berlin", "region": "Berlin", "lat": 52.52, "lon": 13.40},
    "hamburg": {"name": "Hamburg", "region": "Hamburg", "lat": 53.55, "lon": 9.99},
    "muenchen": {"name": "München", "region": "Bayern", "lat": 48.14, "lon": 11.58},
    "koeln": {"name": "Köln", "region": "Nordrhein-Westfalen", "lat": 50.94, "lon": 6.96},
    "frankfurt": {"name": "Frankfurt am Main", "region": "Hessen", "lat": 50.11, "lon": 8.68},
}
