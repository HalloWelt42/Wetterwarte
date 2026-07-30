# Open-Meteo Forecast-API

Die Forecast-API liefert Wettervorhersagen und die aktuellen Bedingungen für beliebige Koordinaten weltweit. Sie ist die Hauptquelle der Wetterwarte für alle Wetterdaten, vom aktuellen Wert über den Stundenverlauf bis zur Sieben-Tage-Vorhersage.

## Basis-URL

```
https://api.open-meteo.com/v1/forecast
```

In der Wetterwarte ist die Basis frei konfigurierbar (Einstellung `open_meteo_base`, Vorgabe `https://api.open-meteo.com/v1`). Der Endpunkt selbst heisst immer `/forecast`. Der öffentliche Dienst ist für nicht-kommerzielle Nutzung ohne Schlüssel erreichbar; die Struktur der Antwort bleibt gleich, wenn später ein selbst gehosteter oder gespiegelter Dienst genutzt wird.

## Grundprinzip

Ein einziger Aufruf kann mehrere Datenbloecke zugleich anfordern. Man gibt pro Block eine kommagetrennte Liste von Variablennamen an:

- `current` - eine Momentaufnahme der Bedingungen zum jetzigen Zeitpunkt
- `hourly` - stündliche Werte über den gesamten Vorhersagezeitraum
- `daily` - taegliche Kennwerte (Hoch, Tief, Summe, Sonnenzeiten)
- `minutely_15` - Werte im 15-Minuten-Raster (nur Mitteleuropa und Nordamerika), für den Kurzfristregen (Nowcast)

Die Antwort enthält zu jedem angeforderten Block ein Zeit-Array (`time`) und je Variable ein gleich langes Werte-Array. Der zeitliche Bezug ergibt sich also aus der Position im Array. Zusätzlich liefert die API zu jedem Block ein Einheiten-Objekt (etwa `hourly_units`), das die tatsaechliche Einheit jeder Variable nennt.

## Parameter

| Parameter | Pflicht | Vorgabe | Werte / Bereich | Bedeutung |
|-----------|---------|---------|-----------------|-----------|
| `latitude` | ja | - | -90 bis 90 | Geografische Breite (WGS84). Kommagetrennte Liste für mehrere Orte möglich. |
| `longitude` | ja | - | -180 bis 180 | Geografische Laenge (WGS84). Negativ für westliche Laengen. |
| `current` | nein | - | Namen von Stundenvariablen | Fordert eine Momentaufnahme der genannten Größen an. |
| `hourly` | nein | - | Namen von Stundenvariablen | Fordert stündliche Verlaeufe an. |
| `daily` | nein | - | Namen von Tagesvariablen | Fordert Tageskennwerte an. Benoetigt sinnvollerweise eine gesetzte `timezone`. |
| `minutely_15` | nein | - | Namen geeigneter Variablen | Werte im 15-Minuten-Raster (regional begrenzt). |
| `timezone` | nein | `GMT` | IANA-Kölnonenname oder `auto` | Wandelt Zeitstempel in die lokale Zeit. `auto` waehlt die Kölnone anhand der Koordinaten. |
| `forecast_days` | nein | 7 | 0 bis 16 | Laenge der Vorhersage in Tagen. |
| `past_days` | nein | 0 | 0 bis 92 | Fuegt vergangene Tage vor dem heutigen Tag hinzu. |
| `wind_speed_unit` | nein | `kmh` | `kmh`, `ms`, `mph`, `kn` | Einheit für Windgeschwindigkeit und Boeen. |
| `temperature_unit` | nein | `celsius` | `celsius`, `fahrenheit` | Einheit für alle Temperaturen. |
| `precipitation_unit` | nein | `mm` | `mm`, `inch` | Einheit für Niederschlagsmengen. |
| `timeformat` | nein | `iso8601` | `iso8601`, `unixtime` | Format der Zeitstempel. |
| `models` | nein | `auto` (Best match) | z. B. `icon_seamless`, `icon_global` | Erzwingt ein bestimmtes Wettermodell statt der automatischen Auswahl. |
| `elevation` | nein | automatisch | Zahl oder `nan` | Ueberschreibt die Hoehenlage. `nan` schaltet die Hoehenkorrektur ab. |
| `cell_selection` | nein | `land` | `land`, `sea`, `nearest` | Strategie zur Wahl der Gitterzelle. |

Hinweis zur Kölnone: Ohne gesetzte `timezone` liefert die API alle Zeiten in UTC (GMT). Für korrekte Tagesgrenzen (Hoch/Tief, Sonnenauf- und -untergang) sollte immer eine Kölnone angegeben werden. Die Wetterwarte setzt fest `Europe/Berlin`.

## Wichtige Variablen

Die folgenden Größen stehen wahlweise in `current`, `hourly` und teils `daily` zur Verfuegung. Die Einheit gilt für die Vorgabe-Einheiten; per Parameter kann sie geaendert werden.

### Aktuell und stündlich

| Variable | Einheit | Bedeutung |
|----------|---------|-----------|
| `temperature_2m` | Grad C | Lufttemperatur in 2 m Hoehe. |
| `relative_humidity_2m` | Prozent | Relative Luftfeuchte in 2 m Hoehe. |
| `dew_point_2m` | Grad C | Taupunkt in 2 m Hoehe. |
| `apparent_temperature` | Grad C | Gefuehlte Temperatur (beruecksichtigt Wind, Feuchte, Sonne). |
| `weather_code` | WMO-Code | Numerischer Wettercode (siehe Tabelle unten). |
| `wind_speed_10m` | km/h | Windgeschwindigkeit in 10 m Hoehe. |
| `wind_direction_10m` | Grad (0 bis 360) | Windrichtung, aus der der Wind weht. 0 = Nord, 90 = Ost. |
| `wind_gusts_10m` | km/h | Boeen (Maximum der vorangehenden Stunde). |
| `precipitation` | mm | Gesamtniederschlag der vorangehenden Stunde (Regen + Schauer + Schnee als Wasseraequivalent). |
| `rain` | mm | Anteil aus grossflaechigem Regen. |
| `showers` | mm | Anteil aus konvektiven Schauern. |
| `snowfall` | cm | Neuschneemenge der vorangehenden Stunde. |
| `precipitation_probability` | Prozent | Regenwahrscheinlichkeit (nur `hourly`, aus Ensemble-Berechnung). |
| `pressure_msl` | hPa | Luftdruck auf Meereshoehe reduziert. |
| `surface_pressure` | hPa | Luftdruck auf tatsaechlicher Standorthoehe. |
| `cloud_cover` | Prozent | Gesamtbewoelkung. |
| `cloud_cover_low` / `_mid` / `_high` | Prozent | Bewoelkung in niedriger, mittlerer, hoher Schicht. |
| `visibility` | Meter | Sichtweite (nur `hourly`). |
| `uv_index` | Index | UV-Index (beginnt bei 0, hoehere Werte bedeuten staerkere UV-Strahlung). |
| `is_day` | 0 oder 1 | 1 = Tag (Sonne über dem Horizont), 0 = Nacht. |

### Täglich

| Variable | Einheit | Bedeutung |
|----------|---------|-----------|
| `temperature_2m_max` / `_min` | Grad C | Tageshoechst- und Tagestiefstwert. |
| `apparent_temperature_max` / `_min` | Grad C | Gefuehlte Temperatur, Tagesextrem. |
| `weather_code` | WMO-Code | Kennzeichnender (schwerster) Wettercode des Tages. |
| `precipitation_sum` | mm | Niederschlagssumme des Tages. |
| `rain_sum` / `showers_sum` / `snowfall_sum` | mm / mm / cm | Tagessummen nach Art. |
| `precipitation_probability_max` | Prozent | Hoechste Regenwahrscheinlichkeit des Tages. |
| `precipitation_hours` | Stunden | Anzahl der Stunden mit Niederschlag. |
| `sunrise` / `sunset` | ISO 8601 | Zeitpunkt von Sonnenaufgang und -untergang. |
| `daylight_duration` | Sekunden | Laenge des lichten Tages. |
| `sunshine_duration` | Sekunden | Dauer direkter Sonneneinstrahlung. |
| `wind_speed_10m_max` / `wind_gusts_10m_max` | km/h | Hoechste Windgeschwindigkeit bzw. Boee des Tages. |
| `wind_direction_10m_dominant` | Grad | Vorherrschende Windrichtung. |
| `uv_index_max` | Index | Hoechster UV-Index des Tages. |

## WMO-Wettercodes

Der `weather_code` folgt dem WMO-Schema 4677. Open-Meteo verwendet daraus die folgenden Werte im Bereich 0 bis 99; andere Codes dieses Bereichs kommen in der Antwort nicht vor. Der Code beschreibt den Wetterzustand; er unterscheidet nicht zwischen Tag und Nacht (dafuer dient `is_day`).

| Code | Bedeutung |
|------|-----------|
| 0 | Klarer Himmel |
| 1 | Ueberwiegend klar |
| 2 | Teils bewoelkt |
| 3 | Bedeckt |
| 45 | Nebel |
| 48 | Nebel mit Reifansatz |
| 51 | Leichter Nieselregen |
| 53 | Maessiger Nieselregen |
| 55 | Dichter Nieselregen |
| 56 | Leichter gefrierender Nieselregen |
| 57 | Dichter gefrierender Nieselregen |
| 61 | Leichter Regen |
| 63 | Maessiger Regen |
| 65 | Starker Regen |
| 66 | Leichter gefrierender Regen |
| 67 | Starker gefrierender Regen |
| 71 | Leichter Schneefall |
| 73 | Maessiger Schneefall |
| 75 | Starker Schneefall |
| 77 | Schneegriesel |
| 80 | Leichte Regenschauer |
| 81 | Maessige Regenschauer |
| 82 | Heftige Regenschauer |
| 85 | Leichte Schneeschauer |
| 86 | Starke Schneeschauer |
| 95 | Gewitter (leicht bis maessig) |
| 96 | Gewitter mit leichtem Hagel |
| 99 | Gewitter mit starkem Hagel |

Hinweis: Die Hagel-Codes 96 und 99 werden nur für Mitteleuropa zuverlässig ausgegeben.

## Wettermodelle für Deutschland

In der Vorgabe (`models=auto`, intern Best match genannt) waehlt Open-Meteo je Ort automatisch das hoechstaufgeloeste passende Modell. Für Deutschland und Mitteleuropa sind das die ICON-Modelle des Deutschen Wetterdienstes (DWD):

- `icon_global` - weltweites Modell, grobere Aufloesung
- `icon_eu` - Europa-Ausschnitt, hoehere Aufloesung
- `icon_d2` - Deutschland und Umgebung, feinste Aufloesung (rund 2 km)

Die automatische Auswahl kombiniert diese zum `icon_seamless` und liefert nahe am Standort die feinste verfuegbare Aufloesung. Für die Wetterwarte in Deutschland bedeutet das: die Werte stammen im Kern von den DWD-ICON-Modellen. Eine manuelle Festlegung über `models` ist möglich, aber für den Regelbetrieb nicht noetig.

## Beispiel-Aufruf

```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=Europe/Berlin&forecast_days=7&wind_speed_unit=kmh"
```

## Beispiel-Antwort (gekuerzt)

```json
{
  "latitude": 52.52,
  "longitude": 13.419,
  "elevation": 44.8,
  "generationtime_ms": 2.2,
  "utc_offset_seconds": 7200,
  "timezone": "Europe/Berlin",
  "timezone_abbreviation": "CEST",
  "current": {
    "time": "2026-07-30T12:00",
    "temperature_2m": 24.3,
    "weather_code": 2,
    "wind_speed_10m": 11.5
  },
  "current_units": {
    "temperature_2m": "°C",
    "weather_code": "wmo code",
    "wind_speed_10m": "km/h"
  },
  "hourly": {
    "time": ["2026-07-30T00:00", "2026-07-30T01:00"],
    "temperature_2m": [17.1, 16.6],
    "precipitation_probability": [0, 5],
    "weather_code": [0, 1]
  },
  "daily": {
    "time": ["2026-07-30", "2026-07-31"],
    "weather_code": [2, 61],
    "temperature_2m_max": [25.4, 22.1],
    "temperature_2m_min": [14.2, 13.8],
    "sunrise": ["2026-07-30T05:41", "2026-07-31T05:43"],
    "sunset": ["2026-07-30T21:02", "2026-07-31T21:00"]
  }
}
```

## Grenzen, Aktualisierung und Frische

- Vorhersagelaenge: bis zu 16 Tage (`forecast_days`), Vergangenheit bis zu 92 Tage (`past_days`). Die Wetterwarte nutzt 7 Tage Vorhersage.
- Modelllaufe: Die DWD-ICON-Modelle werden mehrmals täglich neu gerechnet (Global etwa alle 3 Stunden, das feine `icon_d2` haeufiger). Neue Werte stehen also nicht sekundengenau, sondern im Takt der Modelllaufe zur Verfuegung. Haeufiger als der Modelllauf abzufragen bringt keine neuen Daten.
- Der Zeitstempel `current.time` und das Feld `generationtime_ms` in der Antwort helfen einzuschaetzen, wie frisch die Daten sind.
- Faire Nutzung: Der öffentliche Dienst ist für nicht-kommerzielle Nutzung ohne Schlüssel gedacht und begrenzt die Anfragezahl (Richtwert im niedrigen Tausenderbereich pro Tag). Deshalb sollte die Wetterwarte nicht bei jedem Seitenaufruf direkt bei Open-Meteo anfragen, sondern die Daten zwischenspeichern und im Hintergrund periodisch auffrischen.
- Fehlerfall: Bei ungueltigen Parametern antwortet die API mit HTTP 400 und einem JSON-Objekt `{"error": true, "reason": "..."}`. Fehlende Einzelwerte können im Werte-Array `null` sein und müssen abgefangen werden.

## Nutzung in der Wetterwarte

Die Wetterwarte fragt die Forecast-API zentral im Hintergrund ab und stellt die aufbereiteten Daten dem Frontend bereit. Der Hintergrunddienst (Recorder) frischt die Daten je hinterlegtem Ort alle 10 Minuten auf; die tatsaechliche Neuheit richtet sich aber nach dem Takt der Modelllaufe (siehe oben).

Der Provider (`backend/src/wetterwarte/providers/openmeteo.py`) stellt zwei Abfragen:

Vollabruf (`komplett`) mit einem einzigen Aufruf. Angeforderte Bloecke und Variablen:

- `current`: `temperature_2m`, `relative_humidity_2m`, `apparent_temperature`, `weather_code`, `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`, `pressure_msl`, `cloud_cover`, `dew_point_2m`, `uv_index`, `is_day`
- `hourly`: `temperature_2m`, `weather_code`, `precipitation_probability`, `visibility`, `is_day`
- `minutely_15`: `precipitation`
- `daily`: `weather_code`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_probability_max`, `sunrise`, `sunset`
- feste Zusaetze: `timezone=Europe/Berlin`, `forecast_days=7`, `wind_speed_unit=kmh`

Historie (`historie`) für die Erst-Befuellung des Temperaturarchivs: `hourly=temperature_2m` mit `past_days=30` und `forecast_days=1`.

So landen die Bloecke in der Oberflaeche:

- Aktuell: aus `current` werden Temperatur, gefuehlte Temperatur, Luftfeuchte, Wind mit Richtung, Boeen, Druck, Taupunkt, Bewoelkung und UV gebildet. Die Sichtweite kommt aus dem `hourly`-Block zur aktuellen Stunde. Der `weather_code` wird zusammen mit `is_day` in ein Symbol und einen deutschen Text uebersetzt.
- Stündlich: die kommenden rund 18 Stunden als Verlauf mit Symbol, Temperatur und Regenwahrscheinlichkeit.
- Täglich: die Sieben-Tage-Vorhersage mit Hoch, Tief, Wettersymbol und maximaler Regenwahrscheinlichkeit; zusätzlich Sonnenauf- und -untergang aus dem ersten Tag.
- Nowcast: aus `minutely_15.precipitation` werden die nächsten 3 Stunden im 15-Minuten-Raster ausgewertet, um einen Kurztext (etwa "Regen in 30 Minuten") und eine kleine Balkengrafik zu erzeugen.

Die Basis-URL ist bewusst konfigurierbar gehalten, damit später ein selbst gehosteter Open-Meteo-Dienst genutzt werden kann, ohne die restliche App zu ändern.
