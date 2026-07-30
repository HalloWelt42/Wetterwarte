# Open-Meteo Air-Quality-API

Liefert kostenlose Luftqualitäts- und Pollendaten (Schadstoffkonzentrationen, europäischer Luftqualitätsindex und Pollenflug) für beliebige Koordinaten in Europa und weltweit. In der Wetterwarte speist sie die Kacheln für Luftqualität und Pollenbelastung.

## Basis-URL

```
https://air-quality-api.open-meteo.com/v1/air-quality
```

Der Aufruf erfolgt per HTTP GET. Es wird kein Schlüssel benötigt, solange die Nutzung nicht kommerziell ist. Für gewerbliche Nutzung stellt Open-Meteo kostenpflichtige Zugänge mit eigenem `apikey` bereit.

## Pflichtparameter

Diese beiden Parameter müssen immer angegeben werden:

- `latitude` - geografische Breite (Dezimalgrad, WGS84), z. B. `52.52`
- `longitude` - geografische Länge (Dezimalgrad, WGS84), z. B. `13.41`

Mehrere Standorte lassen sich abfragen, indem man beide Werte als kommagetrennte Liste übergibt (z. B. `latitude=52.52,48.13`). Die Antwort ist dann ein Array mit einem Objekt je Standort.

## Auswahl der Messwerte

Man wählt selbst aus, welche Werte geliefert werden sollen. Es gibt zwei getrennte Listen:

- `current` - eine kommagetrennte Liste von Werten für den aktuellen Zeitpunkt (jüngster verfügbarer Modellwert)
- `hourly` - eine kommagetrennte Liste von Werten als Stundenverlauf (Vergangenheit und Vorhersage)

Beide Listen akzeptieren dieselben Variablennamen. Wird keine der beiden angegeben, liefert die API nur die Kopfdaten ohne Messwerte.

### Wichtige Parameter für die Wetterwarte

Für die Kacheln in der Wetterwarte werden folgende Variablen genutzt (jeweils über `current` abrufbar):

| Variablenname | Bedeutung | Einheit |
|---|---|---|
| `european_aqi` | Europäischer Luftqualitätsindex (Gesamtwert) | Indexwert (EAQI, 0 bis über 100) |
| `pm2_5` | Feinstaub, Partikel kleiner als 2,5 µm | µg/m³ |
| `pm10` | Feinstaub, Partikel kleiner als 10 µm | µg/m³ |
| `ozone` | Bodennahes Ozon (O3) | µg/m³ |
| `nitrogen_dioxide` | Stickstoffdioxid (NO2) | µg/m³ |
| `grass_pollen` | Gräserpollen | grains/m³ (Pollenkörner je m³ Luft) |
| `birch_pollen` | Birkenpollen | grains/m³ |
| `alder_pollen` | Erlenpollen | grains/m³ |
| `mugwort_pollen` | Beifußpollen | grains/m³ |
| `ragweed_pollen` | Ambrosiapollen (Traubenkraut) | grains/m³ |

Hinweis: Pollendaten sind nur für Europa verfügbar und werden nur für die kommenden vier Tage berechnet. Außerhalb Europas fehlen diese Felder oder sind `null`.

### Weitere häufig genutzte Variablen (optional)

Über die Pflicht der Wetterwarte hinaus stehen unter anderem zur Verfügung:

- `sulphur_dioxide` - Schwefeldioxid (SO2), µg/m³
- `carbon_monoxide` - Kohlenmonoxid (CO), µg/m³
- `ammonia` - Ammoniak (NH3), µg/m³ (nur Europa)
- `dust` - Saharastaub, µg/m³
- `aerosol_optical_depth` - Trübung der Atmosphäre bei 550 nm, dimensionslos
- `uv_index` und `uv_index_clear_sky` - UV-Index (mit bzw. ohne Bewölkung)
- `olive_pollen` - Olivenpollen, grains/m³ (nur Europa)
- `us_aqi` - US-amerikanischer Luftqualitätsindex (0 bis 500) samt Teilindizes je Schadstoff (`us_aqi_pm2_5`, `us_aqi_ozone` usw.)
- `european_aqi_pm2_5`, `european_aqi_pm10`, `european_aqi_ozone`, `european_aqi_nitrogen_dioxide`, `european_aqi_sulphur_dioxide` - die einzelnen Teilindizes, aus denen sich der europäische Gesamtindex zusammensetzt

## Zeit- und Steuerparameter

- `timezone` - Kölnone der Zeitstempel, z. B. `Europe/Berlin`. Standard ist `GMT`. Mit `auto` wählt die API die Kölnone anhand der Koordinaten.
- `timeformat` - `iso8601` (Standard, z. B. `2026-07-30T02:00`) oder `unixtime` (Sekunden seit 1970).
- `forecast_days` - Anzahl der Vorhersagetage, 0 bis 7 (Standard 5). Pollen decken davon nur die ersten vier Tage ab.
- `past_days` - Anzahl vergangener Tage im Stundenverlauf, 0 bis 92 (Standard 0).
- `start_date` und `end_date` - fester Zeitraum im Format `yyyy-mm-dd` statt gleitender Tageszahl.
- `domains` - Datenquelle: `auto` (Standard, wählt automatisch), `cams_europe` (feineres Europa-Modell) oder `cams_global` (weltweit).
- `cell_selection` - Auswahl der Modellzelle: `nearest` (Standard), `land` oder `sea`.

## Bedeutung des europäischen Luftqualitätsindex (EU-AQI)

Der europäische Luftqualitätsindex (`european_aqi`) fasst die Belastung durch mehrere Schadstoffe zu einem einzigen Wert zusammen. Der ungünstigste Teilindex bestimmt den Gesamtwert. Er reicht von 0 (sehr saubere Luft) bis über 100 (extreme Belastung). Die Stufen mit den üblichen Farben:

| Indexbereich | Stufe | Farbe (Richtwert) |
|---|---|---|
| 0 bis 20 | Gut | Grün |
| 20 bis 40 | Ausreichend | Gelbgrün |
| 40 bis 60 | Mäßig | Gelb |
| 60 bis 80 | Schlecht | Rot |
| 80 bis 100 | Sehr schlecht | Dunkelrot |
| über 100 | Extrem schlecht | Violett / Bordeaux |

Der Gesamtindex entsteht aus den Teilindizes für Feinstaub (PM2.5, PM10), Stickstoffdioxid, Ozon und Schwefeldioxid. Zur Einordnung die Konzentrationsgrenzen, ab denen ein Schadstoff die jeweilige Stufe erreicht (Feinstaub als Mittel über 24 Stunden, Gase als Stundenwert):

| Schadstoff | Gut | Ausreichend | Mäßig | Schlecht | Sehr schlecht | Extrem schlecht |
|---|---|---|---|---|---|---|
| PM2.5 (µg/m³) | 0-10 | 10-20 | 20-25 | 25-50 | 50-75 | 75-800 |
| PM10 (µg/m³) | 0-20 | 20-40 | 40-50 | 50-100 | 100-150 | 150-1200 |
| NO2 (µg/m³) | 0-40 | 40-90 | 90-120 | 120-230 | 230-340 | 340-1000 |
| O3 (µg/m³) | 0-50 | 50-100 | 100-130 | 130-240 | 240-380 | 380-800 |
| SO2 (µg/m³) | 0-100 | 100-200 | 200-350 | 350-500 | 500-750 | 750-1250 |

## Pollen-Einheiten und Einordnung

Pollenwerte werden in `grains/m³` angegeben, also Pollenkörner je Kubikmeter Luft. Die API liefert reine Konzentrationen ohne fertige Belastungsstufe. Eine gängige, grobe Einteilung für die Anzeige (Werte je nach Pollenart etwas unterschiedlich, hier als allgemeiner Richtwert):

- 0 - keine Belastung
- 1 bis 20 - geringe Belastung
- 20 bis 100 - mittlere Belastung
- über 100 - hohe Belastung

Für die Wetterwarte werden diese Schwellen in eigenen Stufen mit passenden Farben umgesetzt, da die API selbst keine Kategorie mitliefert.

## Beispiel-Aufruf

```bash
curl "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&current=european_aqi,pm2_5,pm10,ozone,nitrogen_dioxide,grass_pollen,birch_pollen,alder_pollen,mugwort_pollen,ragweed_pollen&timezone=Europe/Berlin"
```

## Beispiel-Antwort (gekürzt)

```json
{
  "latitude": 52.5,
  "longitude": 13.400002,
  "generationtime_ms": 0.463,
  "utc_offset_seconds": 7200,
  "timezone": "Europe/Berlin",
  "timezone_abbreviation": "GMT+2",
  "elevation": 38.0,
  "current_units": {
    "time": "iso8601",
    "interval": "seconds",
    "european_aqi": "EAQI",
    "pm2_5": "μg/m³",
    "pm10": "μg/m³",
    "ozone": "μg/m³",
    "nitrogen_dioxide": "μg/m³",
    "grass_pollen": "grains/m³",
    "birch_pollen": "grains/m³",
    "alder_pollen": "grains/m³",
    "mugwort_pollen": "grains/m³",
    "ragweed_pollen": "grains/m³"
  },
  "current": {
    "time": "2026-07-30T02:00",
    "interval": 3600,
    "european_aqi": 20,
    "pm2_5": 7.1,
    "pm10": 11.8,
    "ozone": 50.0,
    "nitrogen_dioxide": 10.7,
    "grass_pollen": 5.2,
    "birch_pollen": 0.0,
    "alder_pollen": 0.0,
    "mugwort_pollen": 121.9,
    "ragweed_pollen": 0.0
  }
}
```

### Aufbau der Antwort

- Kopfdaten: `latitude`, `longitude`, `elevation` (Höhe der Modellzelle), `timezone`, `utc_offset_seconds` sowie `generationtime_ms` (Rechenzeit auf dem Server).
- `current` - Objekt mit dem Zeitstempel `time`, dem Feld `interval` (Abstand der Modellschritte in Sekunden, hier 3600 = ein Stundenschritt) und je einem Feld pro angefragter Variable.
- `current_units` - zugehörige Einheiten je Feld.
- Bei einer Anfrage mit `hourly` kommen zusätzlich die Objekte `hourly` (mit `time` als Array und je Variable ein gleich langes Array) und `hourly_units` hinzu.

Fehlt ein Wert (etwa Pollen außerhalb Europas), steht dort `null`.

## Grenzen, Aktualisierung und Frische

- Datengrundlage in Europa ist das CAMS-Europa-Modell mit rund 0,1° Auflösung (etwa 11 km). Es wird täglich aktualisiert und reicht bis vier Tage in die Zukunft. Weltweit greift das gröbere CAMS-Global-Modell mit rund 0,4° (etwa 45 km) und Aktualisierung alle zwölf Stunden.
- Pollen gibt es nur in Europa und nur als Vier-Tage-Vorhersage. Ammoniak ist ebenfalls auf Europa beschränkt.
- Die Schadstoffwerte liegen als Stundenwerte vor. Der `current`-Wert ist der jüngste Stundenwert des Modells, nicht eine Live-Messung an einer Station. Es handelt sich um Modellvorhersagen, nicht um Sensormessungen.
- Die kostenlose Nutzung ist auf nicht-kommerzielle Zwecke ausgelegt. Open-Meteo empfiehlt einen fairen Umgang mit der Abfragehäufigkeit (Richtwert der Freinutzung: einige Tausend Aufrufe pro Tag). Für die Wetterwarte bedeutet das: Antworten zwischenspeichern und nicht bei jedem Seitenaufruf neu abfragen.

## Hinweise zur Nutzung in der Wetterwarte

- Die Wetterwarte fragt pro Standort einen einzigen `current`-Aufruf mit allen oben genannten Feldern ab und verteilt die Werte auf zwei Kacheln: eine Kachel Luftqualität (EU-AQI plus PM2.5, PM10, Ozon, NO2) und eine Kachel Pollen (Gräser, Birke, Erle, Beifuß, Ambrosia).
- Immer `timezone=Europe/Berlin` (oder `auto`) mitgeben, damit der Zeitstempel zur Ortszeit der Anzeige passt.
- Den `european_aqi` in der Kachel nach den oben genannten Stufen und Farben einfärben; den Zahlenwert zusätzlich als Text zeigen.
- Pollenwerte selbst in Stufen umrechnen (die API liefert nur die Konzentration) und außerhalb Europas oder bei `null` die Pollen-Kachel ausgrauen oder ausblenden, statt einen leeren Wert zu zeigen.
- Antworten serverseitig zwischenspeichern (Frische im Stundenbereich genügt, da die Modelldaten stündlich bzw. täglich aktualisiert werden) und bei einem Ausfall der API den zuletzt gültigen Wert mit Zeitstempel weiter anzeigen.
