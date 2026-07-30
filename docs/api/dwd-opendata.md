# Deutscher Wetterdienst - OpenData und GeoServer

Zweck: Diese Seite beschreibt die frei nutzbaren Wetter- und Klimadaten des Deutschen Wetterdienstes (DWD) und wie die Wetterwarte daraus amtliche Warnungen, Niederschlagsradar und Pollenflug bezieht. Sie ist eine Praxisreferenz für die konkreten Endpunkte, Formate und Aktualisierungsraten - keine vollständige Wiedergabe der amtlichen Dokumentation.

## Überblick und Basis-URLs

Der DWD stellt seine Daten seit 2017 kostenfrei bereit. Es gibt zwei Zugangswege:

| Zweck | Basis-URL | Technik |
| --- | --- | --- |
| Rohdaten-Dateiablage (Vorhersagen, Beobachtungen, Radar, Warnungen, Pollen) | `https://opendata.dwd.de/` | Offener HTTPS-Verzeichnisbaum, kein Login |
| Fertige Geodienste (Karten und abfragbare Warnpolygone) | `https://maps.dwd.de/geoserver/` | OGC WFS und WMS (GeoServer) |

Gemeinsame Eigenschaften:

- Keine Anmeldung, kein API-Schlüssel, keine Kontingente pro Nutzer. Zugriff nur über HTTPS.
- Die Dateiablage ist ein schlichter Verzeichnis-Index (wie ein offener Ordner im Browser). Man navigiert die Ordner entlang und lädt einzelne Dateien.
- Namensnennung ist Pflicht. Bei Weitergabe oder Anzeige der Daten muss die Quelle genannt werden, zum Beispiel "Datenbasis: Deutscher Wetterdienst". Bei Veränderung der Daten ist ein Änderungshinweis zu ergänzen.
- Ein aussagekräftiger `User-Agent` im HTTP-Aufruf wird empfohlen; Aufrufe höflich takten (nur so oft abrufen, wie sich die Daten tatsächlich ändern).

Die folgenden Abschnitte behandeln die fünf für die Wetterwarte wichtigen Produkte: MOSMIX-Vorhersagen, CDC-Stationsbeobachtungen, RADOLAN-Radar, amtliche Warnungen und Pollenflug.

---

## 1. MOSMIX - Punktbezogene Wettervorhersage

MOSMIX ("Model Output Statistics - MIX") ist die statistisch optimierte Punktvorhersage des DWD für über 5000 Stationen weltweit, mit einem Vorhersagehorizont von bis zu 240 Stunden (10 Tage). Ausgeliefert wird sie als KMZ-Datei (ein gezipptes KML im XML-Format mit eigenem DWD-Namensraum).

Basis-URL: `https://opendata.dwd.de/weather/local_forecasts/mos/`

### Zwei Varianten

| Variante | Parameter | Neu erzeugt | Ablage |
| --- | --- | --- | --- |
| MOSMIX_S | ca. 40 | stündlich | nur `all_stations` (eine große Datei je Lauf) |
| MOSMIX_L | ca. 115 | alle 6 Stunden (Läufe 03, 09, 15, 21 UTC) | `all_stations` und `single_stations` (je Station eine kleine Datei) |

Für eine App ist meist MOSMIX_L pro Station am praktischsten: kleine Dateien, stündliche Schritte, viele Parameter, alle 6 Stunden aktualisiert.

### Wichtige Pfade

- Eine Station, jeweils neuester Lauf (empfohlen):
  `https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/single_stations/<STATIONS_ID>/kml/MOSMIX_L_LATEST_<STATIONS_ID>.kmz`
- Alle Stationen, MOSMIX_L: `.../MOSMIX_L/all_stations/kml/`
- Alle Stationen, MOSMIX_S (Dateiname enthält den Lauf-Zeitstempel):
  `.../MOSMIX_S/all_stations/kml/MOSMIX_S_<YYYYMMDDHH>_240.kmz`
- Stationskatalog (Kennung, Name, geographische Lage): im DWD-Bereich "met_verfahren_mosmix" als `mosmix_stationskatalog.cfg`. Die Stations-ID ist die WMO-/DWD-Stationskennung (zum Beispiel `10641` für Offenbach-Wetterpark, `10382` für Berlin-Tempelhof).

### Wichtige Parameter (Elementnamen im KML)

Die Werte stehen als leerzeichengetrennte Liste, ein Wert je Zeitschritt. Ein fehlender Wert ist ein Bindestrich (`-`). Einheiten sind SI-Einheiten:

| Element | Bedeutung | Einheit |
| --- | --- | --- |
| `TTT` | Lufttemperatur 2 m | Kelvin |
| `Td` | Taupunkt 2 m | Kelvin |
| `TX` / `TN` | Maximum / Minimum der Temperatur im Intervall | Kelvin |
| `FF` | Windgeschwindigkeit 10 m | m/s |
| `DD` | Windrichtung | Grad |
| `FX1` | stärkste Böe der letzten Stunde | m/s |
| `RR1c` | Gesamtniederschlag letzte Stunde | kg/m2 (entspricht mm) |
| `wwP` | Niederschlagswahrscheinlichkeit letzte Stunde | Prozent |
| `Neff` / `N` | effektiver Bedeckungsgrad / Gesamtbedeckung | Prozent |
| `PPPP` | Luftdruck (auf Meereshöhe reduziert) | Pascal |
| `Rad1h` | Globalstrahlung letzte Stunde | kJ/m2 |
| `SunD1` | Sonnenscheindauer letzte Stunde | Sekunden |

Hinweis: Temperaturen liegen in Kelvin vor; für die Anzeige in Grad Celsius `TTT - 273.15` rechnen. Die vollständige Elementliste steht in der MOSMIX-Elementdokumentation des DWD.

### Aufbau der KML-Datei

- `<dwd:ForecastTimeSteps>` enthält die Zeitachse: eine Liste von `<dwd:TimeStep>` im ISO-8601-Format (UTC).
- Jede Station ist ein `<kml:Placemark>` mit `<kml:name>` (Stations-ID), Koordinaten und einem Block `<dwd:Forecast dwd:elementName="...">` je Parameter.
- Die Reihenfolge der Werte in `<dwd:value>` entspricht exakt der Reihenfolge der Zeitschritte.

### Beispiel-Aufruf

```bash
curl -A "Wetterwarte/1.0" -o MOSMIX_L_LATEST_10641.kmz \
  "https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/single_stations/10641/kml/MOSMIX_L_LATEST_10641.kmz"

# KMZ ist ein ZIP; das enthaltene KML entpacken:
unzip -p MOSMIX_L_LATEST_10641.kmz > MOSMIX_L_LATEST_10641.kml
```

### Beispiel-Ausschnitt (aus dem entpackten KML)

```xml
<dwd:ForecastTimeSteps>
  <dwd:TimeStep>2026-07-30T00:00:00.000Z</dwd:TimeStep>
  <dwd:TimeStep>2026-07-30T01:00:00.000Z</dwd:TimeStep>
</dwd:ForecastTimeSteps>
...
<kml:Placemark>
  <kml:name>10641</kml:name>
  <kml:ExtendedData>
    <dwd:Forecast dwd:elementName="TTT">
      <dwd:value>291.15 290.35</dwd:value>
    </dwd:Forecast>
    <dwd:Forecast dwd:elementName="RR1c">
      <dwd:value>0.00 0.10</dwd:value>
    </dwd:Forecast>
  </kml:ExtendedData>
</kml:Placemark>
```

### Grenzen, Aktualisierung, Frische

- MOSMIX_S wird stündlich neu erzeugt, MOSMIX_L alle 6 Stunden (Läufe 03/09/15/21 UTC). Die `LATEST`-Datei zeigt immer auf den jeweils jüngsten Lauf.
- Alle Zeitangaben sind UTC.
- Die `all_stations`-Datei von MOSMIX_S ist groß (viele MB), da sie tausende Stationen bündelt. Für wenige Orte immer die Einzelstationsdatei von MOSMIX_L nehmen.
- MOSMIX ist eine Vorhersage, keine Messung. Für aktuelle Ist-Werte siehe Abschnitt 2.

---

## 2. CDC - Stationsbeobachtungen (Messwerte)

Das Climate Data Center (CDC) enthält die tatsächlich gemessenen Beobachtungsdaten der DWD-Stationen in unterschiedlichen zeitlichen Auflösungen (10 Minuten, stündlich, täglich, monatlich, jährlich).

Basis-URL: `https://opendata.dwd.de/climate_environment/CDC/`

### Verzeichnis-Systematik

```
observations_germany/climate/<aufloesung>/<parameter>/<zeitraum>/
```

- `<aufloesung>`: zum Beispiel `10_minutes`, `hourly`, `daily`.
- `<parameter>`: zum Beispiel `air_temperature` (Lufttemperatur und Feuchte), `precipitation` (Niederschlag), `wind`, `pressure`, `cloudiness`, `sun`.
- `<zeitraum>`:
  - `recent/`: die letzten ca. 500 Tage, Qualitätsprüfung noch nicht abgeschlossen, dafür aktuell.
  - `historical/`: geprüft und versioniert, mit Zeitraum im Dateinamen.

Beispiel: `https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/`

### Dateien und Kürzel

Die Stationsdaten liegen als ZIP je Station vor. Das Parameterkürzel steckt im Namen (zum Beispiel `TU` = Temperatur/Feuchte, `RR` = Niederschlag, `FF` = Wind):

- recent: `stundenwerte_TU_<STATIONS_ID5>_akt.zip` (Stations-ID immer 5-stellig mit führenden Nullen, zum Beispiel `00044`).
- historical: `stundenwerte_TU_<ID>_<VON>_<BIS>_hist.zip`.
- Stationsliste je Parameter: `TU_Stundenwerte_Beschreibung_Stationen.txt` (Kennung, Name, Höhe, geographische Lage, Betriebszeitraum).

In jedem ZIP liegt eine `produkt_...txt` mit den eigentlichen Messwerten (semikolongetrennt) sowie Metadaten zur Station.

### Wichtige Antwortfelder (Beispiel stündliche Temperatur, Datei `produkt_tu_stunde_...txt`)

| Spalte | Bedeutung |
| --- | --- |
| `STATIONS_ID` | Stationskennung |
| `MESS_DATUM` | Zeitpunkt im Format `YYYYMMDDHH` (UTC) |
| `QN_9` | Qualitätsniveau der Werte |
| `TT_TU` | Lufttemperatur 2 m in Grad Celsius |
| `RF_TU` | relative Luftfeuchte in Prozent |
| `eor` | Zeilenende-Markierung (End of Record) |

Fehlende Werte sind als `-999` gekennzeichnet. Spalten sind durch `;` getrennt (teils mit umgebenden Leerzeichen).

### Beispiel-Aufruf

```bash
# Stationsliste anzeigen
curl -A "Wetterwarte/1.0" \
  "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/TU_Stundenwerte_Beschreibung_Stationen.txt"

# Messdaten einer Station laden und entpacken (Station 00044)
curl -A "Wetterwarte/1.0" -O \
  "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/stundenwerte_TU_00044_akt.zip"
unzip -o stundenwerte_TU_00044_akt.zip
```

### Beispiel-Ausschnitt (`produkt_tu_stunde_...txt`)

```text
STATIONS_ID;MESS_DATUM;QN_9;TT_TU;RF_TU;eor
         44;2026072812;    1;  18.9;  72.0;eor
         44;2026072813;    1;  20.4;  65.0;eor
```

### Nahezu aktuelle Messwerte (Kurzhinweis)

CDC `recent` hat eine gewisse Verzögerung. Für möglichst frische Ist-Werte je Station gibt es zusätzlich die Kurzberichte unter `https://opendata.dwd.de/weather/weather_reports/poi/` (CSV je Station, Kennung mit Suffix `-BEOB`). Diese enthalten die zuletzt gemeldeten Werte (Temperatur, Wind, Niederschlag, Sicht und weiteres).

### Grenzen, Aktualisierung, Frische

- `recent` deckt rund die letzten 500 Tage ab; längere Reihen ausschließlich in `historical`.
- Zeitstempel sind UTC.
- Qualitätsstufen beachten: `recent`-Werte sind noch nicht endgeprüft.
- Nicht jede Station misst jeden Parameter; die Stationsliste je Parameter ist maßgeblich.

---

## 3. RADOLAN und Radarkomposite - Niederschlag

RADOLAN ("Radar-Online-Aneichung") ist der flächendeckende Niederschlag aus dem DWD-Radarverbund, auf einem deutschlandweiten 1-km-Gitter. Die Daten liegen als binäre Rasterdateien vor (RADOLAN-Binärformat, teils zusätzlich als HDF5/ODIM), meist bz2-komprimiert.

Basis-URL: `https://opendata.dwd.de/weather/radar/`

### Wichtige Produkte

| Pfad | Produkt | Auflösung | Inhalt |
| --- | --- | --- | --- |
| `radolan/rw/` | RW | 1 h Summe | An Stationen angeeichte, stündliche Niederschlagshöhe (das genaueste Standardprodukt) |
| `radolan/ry/` | RY | 5 min | Radar-Niederschlagsrate, nicht angeeicht (Rohqualität, hohe Zeitauflösung) |
| `radolan/yw/` | YW | 5 min | Niederschlagshöhe, aus RY abgeleitet und an RW angeglichen |
| `radolan/sf/` | SF | 24 h Summe | Tagessumme des Niederschlags |
| `composite/rv/` | RV (RADVOR) | 5 min | Kurzfristvorhersage (Nowcast) des Niederschlags bis +2 h |
| `composite/wn/` | WN | 5 min | Reflektivitäts-/Niederschlagsvorhersage bis +2 h |
| `radvor/re/`, `radvor/rq/` | RE, RQ | 1 h | RADVOR-Mengenvorhersagen (angeeicht) |

Weitere Ordner unter `radar/` (zum Beispiel `sites/`, `konrad3d/`, `mesocyclones/`, `composite/hg/`, `composite/pg/`) sind Spezialprodukte und für die Wetterwarte in der Regel nicht nötig.

### Dateinamen und Format

- Namensschema: `raa01-<produkt>_10000-<YYMMDDHHMM>-dwd---bin.bz2` (der Zeitstempel ist UTC). Beispiel: `raa01-rw_10000-2607280010-dwd---bin.bz2`.
- `10000` steht für das deutschlandweite Komposit.
- Das Binärformat besteht aus einem Text-Header (Produkt, Zeit, Gittergröße) und daran anschließenden Rasterwerten. Niederschlagsprodukte sind in 1/10 mm codiert, mit Markierungen für "kein Regen" und "kein Wert" (Fehlkennung).
- Zum Auswerten eignen sich fertige Bibliotheken (zum Beispiel `wradlib` in Python) oder das HDF5-Pendant, falls vorhanden.

### Radar als fertige Karte (WMS)

Wer keine Rohdaten verarbeiten will, bekommt Radarbilder als Kartenkacheln vom GeoServer (siehe auch Abschnitt 4). Beispiel-Layer: `dwd:RX-Produkt` und weitere Radolan-Layer unter `https://maps.dwd.de/geoserver/dwd/wms`.

### Beispiel-Aufruf

```bash
# Neuestes stündliches, angeeichtes Niederschlagskomposit (RW) laden
curl -A "Wetterwarte/1.0" -O \
  "https://opendata.dwd.de/weather/radar/radolan/rw/raa01-rw_10000-2607280010-dwd---bin.bz2"
```

### Beispiel-Ausschnitt (Header, dekomprimiert)

```text
RW260728...10000...BY...GP 900x 900...MS ..<Stationsliste>..
<binäre Rasterwerte>
```

### Grenzen, Aktualisierung, Frische

- RW: neue Datei etwa alle 10 Minuten (fortlaufende stündliche Summe), verfügbar rund 30 Minuten nach Messintervallende; RY/YW/WN/RV im 5-Minuten-Takt.
- Nur Rasterwerte, keine JSON-Struktur. Zum Ablesen eines Ortes muss man dessen Gitterzelle aus den geographischen Koordinaten bestimmen (RADOLAN nutzt eine stereographische Projektion).
- Der Verzeichnis-Index enthält nur ein begrenztes gleitendes Fenster der jüngsten Zeitpunkte; ältere Dateien werden entfernt.
- Alle Zeitangaben UTC.

---

## 4. Amtliche Warnungen (CAP, WFS/WMS, NowCastMIX)

Amtliche Wetterwarnungen gibt es in zwei Ausspielformen: als CAP-Rohdaten in der Dateiablage und als abfragbare Geodienste (WFS/WMS) auf dem GeoServer. CAP ("Common Alerting Protocol") ist ein internationaler XML-Standard für Gefahrenmeldungen.

### 4a. CAP-Rohdaten (Dateiablage)

Basis-URL: `https://opendata.dwd.de/weather/alerts/cap/`

Die Unterordner kombinieren drei Achsen:

- Raumbezug: `COMMUNEUNION` = Gemeindeebene, `DISTRICT` = Landkreisebene.
- Quelle/Typ: `DWD` = amtliche DWD-Warnungen, `EVENT` = ereignisbezogen, `CELLS` = zellbezogen.
- Aktualisierungsart: `STAT` = vollständiger Status (alle aktuell gültigen Warnungen), `DIFF` = nur Änderungen seit dem letzten Stand.

Daraus ergeben sich Ordner wie `COMMUNEUNION_DWD_STAT/`, `DISTRICT_DWD_STAT/`, `COMMUNEUNION_DWD_DIFF/` und so weiter. Für eine App ist meist `COMMUNEUNION_DWD_STAT` (Gemeinde, amtlich, Vollstatus) die richtige Wahl.

Dateien liegen als ZIP mit CAP-XML im Inneren. Es gibt eine `LATEST`-Datei je Sprache:

```
Z_CAP_C_EDZW_LATEST_PVW_STATUS_PREMIUMDWD_COMMUNEUNION_DE.zip   (Deutsch)
Z_CAP_C_EDZW_LATEST_PVW_STATUS_PREMIUMDWD_COMMUNEUNION_EN.zip   (Englisch)
..._FR.zip / ..._ES.zip / ..._MUL.zip (Französisch / Spanisch / mehrsprachig)
```

Wichtige CAP-Felder je Warnung: `identifier`, `sent`, `status`, `msgType`, `scope`, sowie im `info`-Block `category`, `event`, `urgency`, `severity`, `certainty`, `onset`/`effective`/`expires`, `headline`, `description`, `instruction` und im `area`-Block `areaDesc` plus Geocode `WARNCELLID` (die DWD-Warnzellenkennung) und optional ein Polygon.

```bash
curl -A "Wetterwarte/1.0" -O \
  "https://opendata.dwd.de/weather/alerts/cap/COMMUNEUNION_DWD_STAT/Z_CAP_C_EDZW_LATEST_PVW_STATUS_PREMIUMDWD_COMMUNEUNION_DE.zip"
unzip -o Z_CAP_C_EDZW_LATEST_PVW_STATUS_PREMIUMDWD_COMMUNEUNION_DE.zip
```

### 4b. Warnungen als Geodienst (WFS - empfohlen für Apps)

Basis-URL: `https://maps.dwd.de/geoserver/dwd/ows` (gleichwertig `.../dwd/wfs`)

Der WFS liefert die aktuell gültigen Warnungen als fertige Objekte mit Geometrie - ideal, um sie ohne CAP-Parser direkt zu verarbeiten oder auf einer Karte anzuzeigen.

Wichtige `typeName` (Layer):

| typeName | Inhalt |
| --- | --- |
| `dwd:Warnungen_Gemeinden` | Warnungen und Vorabinformationen auf Gemeindeebene |
| `dwd:Warnungen_Gemeinden_vereinigt` | wie oben, benachbarte gleiche Warngebiete zusammengefasst |
| `dwd:Warnungen_Landkreise` | Warnungen auf Landkreisebene |
| `dwd:Warnungen_Kueste` | Warnungen für Küstengebiete |
| `dwd:Warnungen_Binnenseen` | Warnungen für Binnenseen |

Ausgabeformate von `GetFeature` unter anderem: `application/json` (GeoJSON), `GML`, `csv`, `KML`, `SHAPE-ZIP`.

Wichtige Attribute je Feature (identisch benannt zu den CAP-Feldern, in Großbuchstaben): `WARNCELLID`, `NAME`, `AREADESC`, `EVENT`, `HEADLINE`, `DESCRIPTION`, `INSTRUCTION`, `SEVERITY`, `URGENCY`, `CERTAINTY`, `ONSET`, `EXPIRES`, `EFFECTIVE`, `CATEGORY`, `EC_II` (interner Ereigniscode), `EC_AREA_COLOR` (Warnfarbe als "R G B") sowie die Geometrie `THE_GEOM`.

Parameter für den Aufruf:

| Parameter | Bedeutung | Beispiel |
| --- | --- | --- |
| `service` | Dienst | `WFS` |
| `version` | Version | `2.0.0` |
| `request` | Operation | `GetFeature`, `DescribeFeatureType`, `GetCapabilities` |
| `typeName` | Layer | `dwd:Warnungen_Gemeinden` |
| `outputFormat` | Format | `application/json` |
| `count` | Obergrenze der Ergebnisse | `50` |
| `CQL_FILTER` | Filter (Attribut oder Raum) | `WARNCELLID='808117043'` |
| `bbox` | räumlicher Ausschnitt | `minLon,minLat,maxLon,maxLat,EPSG:4326` |

Wichtig: Der Layer enthält nur Gemeinden, für die aktuell eine Warnung gilt. Gibt es keine Warnung, liefert die Abfrage kein Feature. Die Zuordnung Ort zu `WARNCELLID` erfolgt über den DWD-Warncell-Katalog.

Beispiel-Aufruf (Warnungen für eine Warnzelle, als GeoJSON):

```bash
curl -A "Wetterwarte/1.0" \
  "https://maps.dwd.de/geoserver/dwd/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=dwd:Warnungen_Gemeinden&outputFormat=application/json&CQL_FILTER=WARNCELLID='808117043'"
```

Beispiel-Ausschnitt (GeoJSON, gekürzt):

```json
{
  "type": "FeatureCollection",
  "totalFeatures": 1,
  "features": [
    {
      "type": "Feature",
      "properties": {
        "WARNCELLID": "808117043",
        "NAME": "Gemeinde Schlat",
        "EVENT": "STARKE HITZE",
        "SEVERITY": "Minor",
        "URGENCY": "Immediate",
        "CERTAINTY": "Likely",
        "HEADLINE": "Amtliche WARNUNG vor HITZE",
        "ONSET": "2026-07-29T09:00:00Z",
        "EXPIRES": "2026-07-30T17:00:00Z",
        "EC_II": "247",
        "EC_AREA_COLOR": "204 153 255"
      },
      "geometry": { "type": "MultiPolygon", "coordinates": [ ] }
    }
  ]
}
```

Die Warnstufe (Farbe) steckt in `SEVERITY` (CAP: Minor, Moderate, Severe, Extreme) und zusätzlich als RGB-Wert in `EC_AREA_COLOR`.

### 4c. Warnungen als Kartenbild (WMS)

Basis-URL: `https://maps.dwd.de/geoserver/dwd/wms`

Für eine reine Kartendarstellung liefert der WMS fertige Bildkacheln der Warnlagen (und Radar). `GetCapabilities` listet alle Layer (mehrere hundert). Typische Nutzung: `request=GetMap` mit `layers=...`, `bbox`, `width`, `height`, `crs=EPSG:4326`, `format=image/png`, `transparent=true`.

### 4d. NowCastMIX (kurzfristige Unwetterlage)

NowCastMIX ist das automatische Nowcasting-Verfahren des DWD, das aus Radar und Beobachtungen sehr kurzfristige Warnvorschläge für Gewitter, Starkregen und Schneefall erzeugt (Grundlage der AutoWARN-Kette). Die zugehörigen Polygone sind über den GeoServer abrufbar:

| typeName | Inhalt |
| --- | --- |
| `dwd:Autowarn_Analyse` | aktuelle NowCastMIX-Analyse (Ist-Lage signifikanter Wettererscheinungen) |
| `dwd:Autowarn_Vorhersage` | NowCastMIX-Kurzfristvorhersage |

Aufruf analog zu 4b (gleicher WFS, anderer `typeName`).

### Grenzen, Aktualisierung, Frische

- Warnungen ändern sich laufend; die `LATEST`-CAP-Datei und der WFS spiegeln jederzeit den aktuellen Stand. Ein Abruf im Minutentakt reicht in der Regel.
- CAP-`STAT` enthält immer alle gültigen Warnungen (kein Zusammensetzen aus mehreren Dateien nötig); `DIFF` nur für Systeme, die inkrementell mitschreiben.
- Warnzellen (`WARNCELLID`) sind die verbindliche räumliche Einheit.
- Zeitangaben in CAP/WFS sind UTC (mit Kölnonenkennung im Zeitstempel).

---

## 5. Pollenflug-Gefahrenindex (s31fg.json)

Der DWD gibt täglich einen Pollenflug-Gefahrenindex für Deutschland heraus. Er umfasst acht Pollenarten für heute, morgen und übermorgen, aufgeteilt auf 27 Vorhersagegebiete (Regionen und Teilregionen), die sich an Bundesländern und naturräumlichen Gliederungen orientieren.

Endpunkt (eine einzige JSON-Datei): `https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json`

### Aufbau der JSON

Felder auf oberster Ebene:

| Feld | Bedeutung |
| --- | --- |
| `name` | Titel des Produkts |
| `sender` | Herausgeber ("Deutscher Wetterdienst - Medizin-Meteorologie") |
| `last_update` | Zeitpunkt der letzten Ausgabe (deutsche Ortszeit, z. B. `2026-07-28 11:00 Uhr`) |
| `next_update` | Zeitpunkt der nächsten geplanten Ausgabe |
| `legend` | Erklärung der Belastungsstufen (siehe unten) |
| `content` | Liste mit 27 Einträgen, je ein Vorhersagegebiet |

Jeder Eintrag in `content` enthält:

| Feld | Bedeutung |
| --- | --- |
| `region_id` | Kennung der Region (Bundeslandebene) |
| `region_name` | Name der Region, z. B. "Bayern" |
| `partregion_id` | Kennung der Teilregion (`-1`, wenn die Region nicht unterteilt ist) |
| `partregion_name` | Name der Teilregion, z. B. "Mainfranken" (leer, wenn nicht unterteilt) |
| `Pollen` | Objekt mit den acht Pollenarten |

Die acht Pollenarten unter `Pollen`: `Hasel`, `Erle`, `Esche`, `Birke`, `Graeser`, `Roggen`, `Beifuss`, `Ambrosia`. Jede Art hat die Belastungswerte `today`, `tomorrow` und `dayafter_to` (übermorgen).

Hinweis: Die Feldnamen `Graeser` und `Beifuss` stehen in der Datei bewusst ohne Umlaut (JSON-Schlüssel), gemeint sind "Gräser" und "Beifuß".

Belastungsstufen (`legend`), als Text-Codes:

| Wert | Bedeutung |
| --- | --- |
| `0` | keine Belastung |
| `0-1` | keine bis geringe Belastung |
| `1` | geringe Belastung |
| `1-2` | geringe bis mittlere Belastung |
| `2` | mittlere Belastung |
| `2-3` | mittlere bis hohe Belastung |
| `3` | hohe Belastung |

### Beispiel-Aufruf

```bash
curl -A "Wetterwarte/1.0" \
  "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"
```

### Beispiel-Ausschnitt (gekürzt)

```json
{
  "name": "Pollenflug-Gefahrenindex für Deutschland ausgegeben vom Deutschen Wetterdienst",
  "sender": "Deutscher Wetterdienst - Medizin-Meteorologie",
  "last_update": "2026-07-28 11:00 Uhr",
  "next_update": "2026-07-29 11:00 Uhr",
  "legend": { "id1": "0", "id1_desc": "keine Belastung", "id7": "3", "id7_desc": "hohe Belastung" },
  "content": [
    {
      "region_id": 120,
      "region_name": "Bayern",
      "partregion_id": 124,
      "partregion_name": "Mainfranken",
      "Pollen": {
        "Graeser":  { "today": "1", "tomorrow": "1", "dayafter_to": "1" },
        "Beifuss":  { "today": "1", "tomorrow": "1", "dayafter_to": "0-1" },
        "Ambrosia": { "today": "0", "tomorrow": "0", "dayafter_to": "0" }
      }
    }
  ]
}
```

### Grenzen, Aktualisierung, Frische

- Aktualisierung einmal täglich am Vormittag (typischerweise gegen 11 Uhr); `last_update` und `next_update` stehen in der Datei und sind in deutscher Ortszeit angegeben (nicht UTC).
- Es gibt genau 27 Einträge in `content`. Regionen ohne Teilregion tragen `partregion_id = -1` und einen leeren `partregion_name`.
- Der Index ist ein Flächenmittel je Gebiet; kleinräumige oder tageszeitliche Schwankungen bildet er nicht ab. `dayafter_to` (übermorgen) ist die unsicherste Stufe.

---

## Nutzung in der Wetterwarte

Die Wetterwarte bezieht ihre Deutschland-spezifischen Inhalte direkt aus diesen DWD-Quellen und bereitet sie lokal auf (Abruf, Zwischenspeicherung, Anzeige in Kacheln):

- Amtliche Warnungen: bevorzugt über den WFS `dwd:Warnungen_Gemeinden` als GeoJSON (fertige Objekte mit Geometrie, ohne eigenen CAP-Parser). Alternativ die CAP-Rohdaten `COMMUNEUNION_DWD_STAT` für eine quellennahe Verarbeitung. Kurzfristige Unwetter zusätzlich über NowCastMIX (`dwd:Autowarn_Analyse` / `dwd:Autowarn_Vorhersage`).
- Niederschlagsradar: als Kartenlayer über den WMS bzw. für Werte je Ort aus den RADOLAN-Produkten (`rw` für die stündliche Summe, `rv`/`wn` für den Kurzfrist-Nowcast).
- Pollenflug: aus der einen Datei `s31fg.json`, Zuordnung des Ortes zu einer der 27 Regionen/Teilregionen.

Betriebshinweise: Alle Abrufe brauchen keinen Login. Aufrufe im sinnvollen Takt planen (Warnungen minütlich, Radar alle 5 bis 10 Minuten, MOSMIX stündlich bzw. alle 6 Stunden, Pollen einmal täglich anhand von `next_update`). Zeitstempel aus opendata/GeoServer sind UTC (Ausnahme: Pollen-Datei in deutscher Ortszeit) und müssen für die Anzeige in die lokale Kölnone umgerechnet werden. Bei Anzeige der Daten die Quelle nennen: "Datenbasis: Deutscher Wetterdienst".
