# Bright Sky API

Kostenlose JSON-Schnittstelle, die die offenen Rohdaten des Deutschen Wetterdienstes (DWD) aufbereitet und leicht abrufbar macht: Beobachtungen, Vorhersagen, Radar und amtliche Wetterwarnungen. In der Wetterwarte liefert Bright Sky vorerst die amtlichen Unwetterwarnungen über den Endpunkt `/alerts`; die übrigen Endpunkte sind für den späteren Ausbau dokumentiert.

## Basis-URL

```
https://api.brightsky.dev
```

Alle Aufrufe erfolgen per HTTP GET und liefern JSON. Es wird kein Schlüssel benötigt. Für die eigentlichen Wetterdaten gelten die Nutzungsbedingungen des DWD (Quellenangabe erforderlich); die Bright-Sky-Software selbst steht unter der MIT-Lizenz. Fast alle Endpunkte lassen sich alternativ über eine Koordinate (`lat`/`lon`) oder über eine Stationskennung (`dwd_station_id`, `wmo_station_id`, `source_id`) ansteuern.

## Gemeinsame Parameter

Diese Parameter kommen bei mehreren Endpunkten vor und haben überall dieselbe Bedeutung:

- `lat`, `lon` - geografische Breite und Länge in Dezimalgrad (WGS84), z. B. `lat=52.52&lon=13.41`. Bright Sky sucht dann die nächstgelegene passende Station bzw. Warnzelle.
- `dwd_station_id` - Stationskennung des DWD (auch mehrfach angebbar).
- `wmo_station_id` - internationale Stationskennung der Weltorganisation für Meteorologie.
- `source_id` - interne Quellen-ID von Bright Sky (aus dem `sources`-Block einer Antwort).
- `max_dist` - maximaler Suchradius in Metern rund um `lat`/`lon`, Standard `50000` (50 km).
- `tz` - Kölnone der Zeitstempel als Name aus der Kölnonendatenbank, z. B. `Europe/Berlin`. Ohne Angabe werden die Zeitstempel in UTC (mit Offset `+00:00`) geliefert.
- `units` - Einheitensystem, `dwd` (Standard, praxisübliche Einheiten) oder `si` (SI-Einheiten). Betrifft die Wetter-Endpunkte, nicht `/alerts`.

Zeitstempel sind durchgängig im Format ISO 8601 (z. B. `2026-07-30T09:00:00+00:00`).

## /alerts - amtliche Wetterwarnungen (Schwerpunkt)

Liefert die aktuell gültigen und angekündigten Warnungen des DWD für einen Ort. Grundlage ist das amtliche Warnsystem (CAP), aufbereitet als flaches JSON mit zweisprachigen Texten (Deutsch und Englisch).

### Parameter

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `lat`, `lon` | einer von beiden Wegen | Koordinate, für die die zuständige Warnzelle bestimmt wird |
| `warn_cell_id` | einer von beiden Wegen | direkte Angabe der amtlichen Warnzellen-ID (Gemeindekennung), falls schon bekannt |
| `tz` | nein | Kölnone der Zeitstempel, z. B. `Europe/Berlin` |

Es muss entweder `lat` und `lon` oder `warn_cell_id` angegeben werden. Ohne Warnung liefert die API ein leeres Array `"alerts": []` bei ansonsten gefüllter Antwort.

### Wichtige Antwortfelder

Die Antwort besteht aus dem Array `alerts` (eine Warnung je Eintrag) und dem Objekt `location` (die zugeordnete Warnzelle).

Felder je Warnung in `alerts`:

| Feld | Bedeutung |
|---|---|
| `id` | interne, fortlaufende ID der Warnung bei Bright Sky |
| `alert_id` | eindeutige amtliche Kennung der Warnung (CAP-Identifier des DWD) |
| `event_de` / `event_en` | Art des Ereignisses, z. B. `STARKE HITZE` bzw. `strong heat` |
| `event_code` | numerischer Ereigniscode des DWD |
| `headline_de` / `headline_en` | Kurzüberschrift, z. B. `Amtliche WARNUNG vor HITZE` |
| `description_de` / `description_en` | ausführliche Beschreibung der Lage |
| `instruction_de` / `instruction_en` | Handlungsempfehlung für die Bevölkerung (kann leer sein) |
| `severity` | Schweregrad: `minor`, `moderate`, `severe` oder `extreme` (siehe unten) |
| `urgency` | Dringlichkeit: `immediate` (sofort) oder `future` (künftig) |
| `certainty` | Eintrittswahrscheinlichkeit: z. B. `observed`, `likely`, `possible` |
| `category` | thematische Einordnung, z. B. `met` (Wetter) oder `health` (Gesundheit) |
| `response_type` | empfohlene Reaktion, z. B. `prepare` (vorbereiten), `monitor` (beobachten), `none` |
| `onset` | Beginn der Gültigkeit (ab wann die Warnung gilt) |
| `expires` | Ende der Gültigkeit (bis wann die Warnung gilt) |
| `effective` | Zeitpunkt, zu dem die Warnung ausgegeben wurde |
| `status` | Zustand, im Normalbetrieb `actual` (echte Warnung, kein Test) |

Felder im Objekt `location`:

| Feld | Bedeutung |
|---|---|
| `warn_cell_id` | ID der amtlichen Warnzelle |
| `name` / `name_short` | Name der Zelle (lang und kurz) |
| `district` | Landkreis bzw. kreisfreie Stadt |
| `state` / `state_short` | Bundesland (Name und Kürzel) |

### Schweregrade (`severity`)

Der Schweregrad entspricht den vierstufigen Warnstufen des DWD samt der bekannten Ampelfarben:

| `severity` | DWD-Warnstufe | Farbe (Richtwert) |
|---|---|---|
| `minor` | Stufe 1, Wetterwarnung | Gelb |
| `moderate` | Stufe 2, markante Wetterwarnung | Orange |
| `severe` | Stufe 3, Unwetterwarnung | Rot |
| `extreme` | Stufe 4, extreme Unwetterwarnung | Violett / Dunkelrot |

### Beispiel-Aufruf

```bash
curl "https://api.brightsky.dev/alerts?lat=52.52&lon=13.4&tz=Europe/Berlin"
```

### Beispiel-Antwort (gekürzt)

```json
{
  "alerts": [
    {
      "id": 2678791,
      "alert_id": "2.49.0.0.276.0.DWD.PVW.1785309720000.b53d1f87-...",
      "effective": "2026-07-29T07:22:00+00:00",
      "onset": "2026-07-30T09:00:00+00:00",
      "expires": "2026-07-30T17:00:00+00:00",
      "category": "health",
      "response_type": "prepare",
      "urgency": "immediate",
      "severity": "minor",
      "certainty": "likely",
      "event_code": 247,
      "event_en": "strong heat",
      "event_de": "STARKE HITZE",
      "headline_en": "Official WARNING of STRONG HEAT",
      "headline_de": "Amtliche WARNUNG vor HITZE",
      "description_de": "Am Donnerstag wird eine starke Wärmebelastung erwartet. ...",
      "instruction_de": "Hitzebelastung kann für den menschlichen Körper gefährlich werden ...",
      "status": "actual"
    }
  ],
  "location": {
    "warn_cell_id": 711000101,
    "name": "Berl. - Mitte",
    "name_short": "B.-Mitte",
    "district": "Berlin",
    "state": "Berlin",
    "state_short": "BE"
  }
}
```

Hinweis: Die langen Textfelder (`description_de`, `instruction_de`) enthalten in der echten Antwort Zeilenumbrüche (`\n`); oben sind sie zur Lesbarkeit gekürzt.

## /current_weather - aktuelle Messwerte

Liefert den jüngsten verfügbaren Beobachtungswert der nächstgelegenen Station.

Parameter: `lat`/`lon` oder Stationskennung, dazu `max_dist`, `tz`, `units`.

Wichtige Antwortfelder (Objekt `weather`): `timestamp`, `temperature` (Grad Celsius), `relative_humidity` (Prozent), `dew_point` (Taupunkt in Grad Celsius), `pressure_msl` (Luftdruck auf Meereshöhe in hPa), `wind_speed_10`/`wind_direction_10` (Wind über 10 Minuten in km/h bzw. Grad), `wind_gust_speed_10` (Böe), `cloud_cover` (Bewölkung in Prozent), `visibility` (Sichtweite in Metern), `condition` (Wetterlage, z. B. `dry`, `rain`, `snow`) und `icon` (Vorschlag für ein Wettersymbol, z. B. `clear-night`). Die Suffixe `_10`, `_30`, `_60` stehen für Mittel bzw. Summe über die letzten 10, 30 oder 60 Minuten. Dazu kommt ein `sources`-Array mit den Stationen, aus denen die Werte stammen.

```bash
curl "https://api.brightsky.dev/current_weather?lat=52.52&lon=13.4&tz=Europe/Berlin"
```

```json
{
  "weather": {
    "source_id": 303711,
    "timestamp": "2026-07-30T00:00:00+00:00",
    "temperature": 21.1,
    "relative_humidity": 64,
    "pressure_msl": 1016.7,
    "wind_speed_10": 9.0,
    "wind_direction_10": 120,
    "cloud_cover": 0,
    "condition": "dry",
    "icon": "clear-night"
  },
  "sources": [
    { "id": 303711, "station_name": "Berlin-Tempelhof", "wmo_station_id": "10384", "distance": 5835.0 }
  ]
}
```

## /weather - Verlauf und Vorhersage

Liefert Stundenwerte für einen Zeitraum. Kombiniert Beobachtungen der Vergangenheit mit der MOSMIX-Vorhersage des DWD für die Zukunft.

Parameter: `date` (Pflicht, erster Zeitpunkt, ISO 8601 oder `yyyy-mm-dd`), `last_date` (letzter Zeitpunkt, Standard `date` plus ein Tag), dazu `lat`/`lon` oder Stationskennung, `max_dist`, `tz`, `units`.

Wichtige Antwortfelder je Stunde im Array `weather`: `timestamp`, `temperature`, `precipitation` (Niederschlag in mm), `precipitation_probability` (Regenwahrscheinlichkeit in Prozent, nur Vorhersage), `wind_speed`, `wind_direction`, `wind_gust_speed`, `cloud_cover`, `sunshine` (Sonnenscheindauer in Minuten), `relative_humidity`, `dew_point`, `pressure_msl`, `visibility`, `condition`, `icon`. Fehlende Werte sind `null`.

```bash
curl "https://api.brightsky.dev/weather?lat=52.52&lon=13.4&date=2026-07-30&tz=Europe/Berlin"
```

```json
{
  "weather": [
    {
      "timestamp": "2026-07-30T00:00:00+00:00",
      "temperature": 18.9,
      "precipitation": 0.0,
      "precipitation_probability": 1,
      "wind_speed": 13.0,
      "wind_direction": 128,
      "cloud_cover": 1,
      "condition": "dry",
      "icon": "clear-night"
    }
  ],
  "sources": []
}
```

## /synop - Rohbeobachtungen

Liefert historische Stationsmeldungen (SYNOP) in hoher zeitlicher Auflösung, ohne Vorhersageanteil. Anders als bei den anderen Endpunkten ist die Station Pflicht: Auswahl nur über `dwd_station_id`, `wmo_station_id` oder `source_id`, nicht über `lat`/`lon`.

Parameter: `date` (Pflicht), `last_date`, `dwd_station_id` bzw. `wmo_station_id` bzw. `source_id`, `tz`, `units`.

Die Felder je Eintrag entsprechen `/current_weather` (mit den Suffixen `_10`, `_30`, `_60` für die jeweiligen Zeitfenster), enthalten aber nur echte Messwerte; nicht gemeldete Größen sind `null`.

```bash
curl "https://api.brightsky.dev/synop?wmo_station_id=10384&date=2026-07-30&tz=Europe/Berlin"
```

## /radar - Niederschlagsradar

Liefert die Radar-Niederschlagsdaten des DWD als Gitter in 5-Minuten-Schritten, rund zwei Stunden rückwärts und rund zwei Stunden Kurzfrist-Vorhersage.

Parameter: `lat`/`lon` mit `distance` (Radius in Metern rund um den Punkt, Standard `200000`) oder `bbox` (Bildausschnitt als `[oben, links, unten, rechts]` in Pixeln des DWD-Gitters); dazu `date`, `last_date`, `tz` und `format`. `format` bestimmt die Kodierung des Niederschlagsgitters: `compressed` (Standard, platzsparend base64- und zlib-kodiert), `bytes` (rohe Bytes) oder `plain` (gut lesbares, verschachteltes Zahlen-Array). Die Werte im Feld `precipitation_5` sind Niederschlagsmengen in Einheiten von 0,01 mm je 5 Minuten.

Antwortaufbau: `radar` (Array mit je `timestamp`, `source` und `precipitation_5`) sowie die Gitter-Metadaten `bbox`, `geometry` und `latlon_position` (Pixelposition der angefragten Koordinate im Ausschnitt).

```bash
curl "https://api.brightsky.dev/radar?lat=52.52&lon=13.4&format=plain&distance=1000"
```

```json
{
  "radar": [
    { "timestamp": "2026-07-30T00:00:00+00:00", "source": "RADOLAN::RV::...", "precipitation_5": [[0, 0], [0, 0]] }
  ],
  "bbox": [415, 782, 417, 784],
  "latlon_position": { "x": 1.15, "y": 1.281 }
}
```

## /sources - Stationsverzeichnis

Liefert die Metadaten der Stationen (Quellen), die zu einer Koordinate oder Kennung passen. Nützlich, um eine `source_id` für gezielte Folgeabfragen zu ermitteln.

Parameter: `lat`/`lon` oder Stationskennung, dazu `max_dist`, `tz`.

Wichtige Antwortfelder je Eintrag im Array `sources`: `id` (die `source_id`), `dwd_station_id`, `wmo_station_id`, `station_name`, `observation_type` (Datenart, z. B. `synop`, `current`, `historical`, `forecast`), `lat`, `lon`, `height` (Höhe in Metern), `first_record`, `last_record` (ältester bzw. jüngster verfügbarer Zeitpunkt) und `distance` (Entfernung zur Anfragekoordinate in Metern).

```bash
curl "https://api.brightsky.dev/sources?lat=52.52&lon=13.4"
```

## Grenzen, Aktualisierung und Frische

- Kein Schlüssel nötig, aber es gilt eine faire Nutzung. Bright Sky ist ein kostenloser Gemeinschaftsdienst; Abfragen sollten zwischengespeichert und nicht bei jedem Seitenaufruf neu gestellt werden. Für sehr hohe Lasten empfiehlt der Betreiber eine eigene Instanz (die Software ist quelloffen).
- Warnungen (`/alerts`) werden vom DWD nahezu in Echtzeit ausgegeben und alle paar Minuten aktualisiert. Für die Anzeige genügt ein Abgleich im Minuten- bis Viertelstundentakt. Maßgeblich für die Gültigkeit sind `onset` und `expires`; abgelaufene Warnungen verschwinden aus der Antwort.
- Beobachtungen (`/current_weather`, `/synop`) liegen je nach Station meist in 10- bis 30-Minuten-Schritten vor, mit kurzer Verzögerung. Der Radar (`/radar`) wird alle 5 Minuten fortgeschrieben.
- Vorhersagen (`/weather`) beruhen auf dem MOSMIX-Modell des DWD und werden mehrmals täglich neu berechnet.
- Es handelt sich um DWD-Daten; bei der Weitergabe ist der DWD als Quelle zu nennen.

## Hinweise zur Nutzung in der Wetterwarte

- Die Wetterwarte nutzt `/alerts` als Übergangslösung für amtliche Warnungen. Später ist ein eigener DWD-Ingester geplant, der die Warnungen direkt aus der offenen DWD-Quelle bezieht; die hier beschriebenen Felder dienen dann als Vorlage für das eigene Datenmodell.
- Pro Standort einen Aufruf `/alerts?lat=...&lon=...&tz=Europe/Berlin` absetzen und alle Einträge des `alerts`-Arrays anzeigen; ein leeres Array bedeutet "keine Warnung" und sollte als ruhiger Normalzustand dargestellt werden, nicht als Fehler.
- Die Warn-Kachel nach `severity` einfärben (Gelb, Orange, Rot, Violett) und `headline_de` als Titel sowie `event_de` als Kurzform zeigen; Details aus `description_de` und Handlungsempfehlung aus `instruction_de` erst bei Bedarf einblenden.
- Immer die deutschen Felder (`*_de`) verwenden und `tz=Europe/Berlin` mitgeben, damit `onset` und `expires` in Ortszeit passen. Warnungen, deren `onset` in der Zukunft liegt, als Vorabinformation kennzeichnen.
- Antworten serverseitig kurz zwischenspeichern (Frische im Minutenbereich) und bei einem Ausfall der API den zuletzt bekannten Stand mit Zeitstempel weiter anzeigen, statt die Kachel leer zu lassen.
