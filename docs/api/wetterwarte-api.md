# Wetterwarte-API (eigenes Backend)

Die eigene Backend-Schnittstelle der Wetterwarte (FastAPI). Sie bündelt alle
Wetterdaten eines Ortes zu einer einzigen Antwort, verwaltet die
Dashboard-Layouts und liefert den Langzeit-Verlauf aus dem eigenen Archiv. Das
Frontend spricht ausschließlich mit dieser Schnittstelle; die eigentlichen
Datenquellen sind dahinter gekapselt.

## Basis-URL

```
http://localhost:6169/api/v1
```

Alle Endpunkte liegen unter dem Prefix `/api/v1`. Der Port stammt aus der
Projektkonfiguration (`.env`, Schlüssel `BACKEND_PORT`); die Vorlage
(`.env.example`) verwendet als Standard `6150`, diese Instanz läuft auf `6169`.

Ergänzend gibt es die automatisch erzeugte, interaktive Dokumentation:

- `http://localhost:6169/api/docs` (bedienbare Oberfläche zum Ausprobieren)
- `http://localhost:6169/api/openapi.json` (maschinenlesbare Beschreibung)

## Antwort-Umschlag (Envelope)

Jede erfolgreiche Antwort ist gleich aufgebaut. Die eigentlichen Nutzdaten
stehen immer unter `data`, begleitende Angaben unter `meta`:

```json
{
  "data": { "...": "die eigentlichen Nutzdaten" },
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

- `data` - Nutzdaten des jeweiligen Endpunkts (Objekt oder Liste).
- `meta.version` - Version des Backends, mit der die Antwort erzeugt wurde.
- `meta.platzhalter` - `true`, wenn die Daten nur Platzhalter bzw. Ersatzwerte
  sind (etwa wenn eine Quelle ausfällt). Aktuell liefern alle Endpunkte echte
  Daten (`false`); die Auswertung im Frontend sollte den Fall `true` dennoch
  berücksichtigen.

### Fehler

Fehler folgen nicht dem Envelope, sondern dem FastAPI-Standard mit einem Feld
`detail`:

```json
{ "detail": "Ort nicht bekannt" }
```

Verwendete Status-Codes:

- `404` - angeforderte Ressource unbekannt (z. B. unbekannter Ort oder unbekannte
  Layout-ID).
- `502` - die vorgelagerte Wetterquelle ist nicht erreichbar.
- `422` - ungültige Parameter (z. B. `tage` ist keine Zahl); von FastAPI erzeugt.

---

## GET /health

Kurzer Betriebs- und Bereitschafts-Check. Meldet, dass das Backend läuft, und
nennt seine Version. Ohne Parameter.

Wichtige Antwortfelder:

- `data.status` - immer `"ok"`, wenn das Backend antwortet.
- `data.version` - laufende Backend-Version.

Beispiel-Aufruf:

```bash
curl http://localhost:6169/api/v1/health
```

Beispiel-Antwort:

```json
{
  "data": { "status": "ok", "version": "0.1.0" },
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

---

## GET /weather/complete/{ort}

Liefert alles zu einem Ort in einer einzigen Antwort: aktueller Zustand,
Stundenvorschau, Wochenvorschau, Sonnenzeiten, Regen-Kurzfrist (Nowcast),
amtliche Warnungen, Luftqualität und Live-Blitze. Diese eine Antwort speist das
gesamte Kachel-Dashboard.

Pfadparameter:

- `ort` - Kürzel (Slug) des Ortes, z. B. `koeln`, `frankfurt`, `berlin`,
  `hamburg`, `muenchen`. Die Groß-/Kleinschreibung spielt keine Rolle. Die
  verfügbaren Slugs liefert `GET /weather/orte`. Ist der Ort unbekannt, kommt
  `404`.

Aufbau von `data`:

- `ort` - `{ name, region, lat, lon }` (Anzeigename, Region und Koordinaten).
- `aktuell` - aktueller Zustand, siehe unten.
- `stunden` - Liste von bis zu 18 Stunden ab jetzt.
- `tage` - Liste von bis zu 7 Tagen (Tag 0 ist heute).
- `sonne` - `{ aufgang, untergang }` als `"HH:MM"`.
- `nowcast` - Regen-Kurzfrist der nächsten 3 Stunden oder `null`.
- `luft` - Luftqualität oder `null`.
- `warnungen` - Liste amtlicher Warnungen (kann leer sein).
- `blitze` - Live-Blitze oder `null`.

Felder in `aktuell`:

- `temperatur` - Lufttemperatur in Grad Celsius (gerundet).
- `tempKlasse` - Farbklasse für die Darstellung: eine von `t-frost`, `t-kalt`,
  `t-kuehl`, `t-mild`, `t-warm`, `t-heiss`, `t-extrem`.
- `gefuehlt` - gefühlte Temperatur in Grad Celsius.
- `tageshoch` - heutiges Tageshoch in Grad Celsius.
- `zustandText` - Wetterzustand als deutscher Text (z. B. `"Bedeckt"`).
- `icon` - Name des Wettersymbols (Meteocon-Bezeichnung, z. B.
  `partly-cloudy-night`).
- `feuchte` - relative Luftfeuchte in Prozent.
- `wind` - Windgeschwindigkeit in km/h.
- `windRichtung` - Himmelsrichtung als Kürzel (`N`, `NO`, `O`, `SO`, `S`, `SW`,
  `W`, `NW`).
- `windGrad` - Windrichtung in Grad (0 bis 359).
- `boeen` - Windböen in km/h.
- `druck` - Luftdruck in Hektopascal (hPa).
- `sicht` - Sichtweite in Kilometern, oder `null`, wenn die Quelle keinen Wert
  liefert.
- `taupunkt` - Taupunkt in Grad Celsius.
- `bewoelkung` - Bewölkungsgrad in Prozent.
- `uv` - UV-Index (ganze Zahl).

Felder je Eintrag in `stunden`:

- `zeit` - `"jetzt"` für die laufende Stunde, sonst die Stunde als `"HH"`.
- `icon` - Wettersymbol dieser Stunde.
- `temp` - Temperatur in Grad Celsius.
- `tempKlasse` - Farbklasse (wie oben).
- `regen` - Niederschlagswahrscheinlichkeit in Prozent.

Felder je Eintrag in `tage`:

- `kurz` - `"Heute"` oder Wochentagskürzel (`Mo` bis `So`).
- `icon` - Wettersymbol des Tages.
- `hi` - Tageshöchstwert in Grad Celsius.
- `lo` - Tagestiefstwert in Grad Celsius.
- `regen` - höchste Niederschlagswahrscheinlichkeit des Tages in Prozent.
- `bandLinks`, `bandRechts` - Prozentwerte für den Temperaturbalken, der die
  Tagesspanne innerhalb der Wochenspanne einordnet (linker bzw. rechter
  Abstand). Reine Darstellungshilfe für das Balkendiagramm.

Felder in `nowcast` (oder `null`, wenn keine Kurzfristdaten vorliegen):

- `text` - Klartext, z. B. `"Regen in 30 Minuten"` oder `"Kein Regen in den
  nächsten 3 Stunden"`.
- `balken` - Liste von 12 Werten (0 bis 100) im 15-Minuten-Raster für die
  nächsten 3 Stunden; als Balkenhöhen für die Regen-Kurzfrist gedacht.

Felder in `luft` (oder `null`, wenn die Quelle ausfällt):

- `aqi` - europäischer Luftqualitätsindex (gerundet).
- `label` - Einstufung als Text: `Gut`, `Ordentlich`, `Mäßig`, `Schlecht`,
  `Sehr schlecht` oder `Extrem schlecht`.
- `pm2_5`, `pm10` - Feinstaub in Mikrogramm pro Kubikmeter.
- `o3` - Ozon, `no2` - Stickstoffdioxid (jeweils Mikrogramm pro Kubikmeter).
- `pollen` - Liste `{ name, stufe }`; `name` ist z. B. `Gräser`, `Birke`,
  `Erle`, `Beifuß`, `Ambrosia`, `stufe` ist 0 (keine) bis 3 (hoch).

Felder in `warnungen` (Liste, kann leer sein):

- `stufe` - Warnstufe von 1 (gering) bis 4 (extrem).
- `titel` - Kurztext der Warnung, z. B. `"STARKE HITZE"`.
- `zeit` - Gültigkeitszeitraum als Text, z. B. `"09:00 - 17:00 Uhr"`.

Felder in `blitze` (oder `null`, wenn der Dienst nicht erreichbar ist):

- `anzahl` - Anzahl der Blitze im Umkreis innerhalb der letzten Stunde.
- `liste` - bis zu 3 jüngste Blitze, je `{ zeit, distanz }`, z. B.
  `{ "zeit": "vor 4 Min", "distanz": "12 km SW" }`.

Beispiel-Aufruf:

```bash
curl http://localhost:6169/api/v1/weather/complete/koeln
```

Beispiel-Antwort (gekürzt):

```json
{
  "data": {
    "ort": { "name": "Köln", "region": "Sachsen-Anhalt", "lat": 51.05, "lon": 12.14 },
    "aktuell": {
      "temperatur": 23, "tempKlasse": "t-warm", "gefuehlt": 23, "tageshoch": 37,
      "zustandText": "Überwiegend klar", "icon": "partly-cloudy-night",
      "feuchte": 51, "wind": 6, "windRichtung": "S", "windGrad": 187,
      "boeen": 14, "druck": 1016, "sicht": 42, "taupunkt": 13,
      "bewoelkung": 20, "uv": 0
    },
    "stunden": [
      { "zeit": "jetzt", "icon": "clear-night", "temp": 23, "tempKlasse": "t-warm", "regen": 0 },
      { "zeit": "02", "icon": "partly-cloudy-night", "temp": 23, "tempKlasse": "t-warm", "regen": 0 }
    ],
    "tage": [
      { "kurz": "Heute", "icon": "overcast-day", "hi": 37, "lo": 22, "regen": 18, "bandLinks": 29, "bandRechts": 0 },
      { "kurz": "Fr", "icon": "rain", "hi": 32, "lo": 20, "regen": 58, "bandLinks": 19, "bandRechts": 24 }
    ],
    "sonne": { "aufgang": "05:34", "untergang": "21:01" },
    "nowcast": { "text": "Kein Regen in den nächsten 3 Stunden", "balken": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] },
    "luft": {
      "aqi": 21, "label": "Ordentlich", "pm2_5": 7, "pm10": 12, "o3": 53, "no2": 8,
      "pollen": [ { "name": "Gräser", "stufe": 2 }, { "name": "Birke", "stufe": 0 } ]
    },
    "warnungen": [ { "stufe": 1, "titel": "STARKE HITZE", "zeit": "09:00 - 17:00 Uhr" } ],
    "blitze": null
  },
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

Hinweis zur Robustheit: Die Grunddaten (aktuell, Stunden, Tage, Sonne, Nowcast)
stammen aus einer Hauptquelle. Fällt diese aus, antwortet der Endpunkt mit
`502`. Die Zusatzquellen (Luftqualität, Warnungen, Blitze) sind abgesichert:
Fällt eine aus, wird die Antwort nicht abgebrochen, sondern das jeweilige Feld
ist `null` (bei Warnungen eine leere Liste). Die Live-Blitze kommen von einem
Dienst im lokalen Netz und sind deshalb oft `null`, wenn dieser nicht erreichbar
ist.

---

## GET /weather/orte

Liefert die bekannten Orte (Kürzel plus Anzeigename, Region und Koordinaten).
Ohne Parameter. Dient dazu, die Ortsauswahl zu füllen und gültige Slugs für
`/weather/complete/{ort}` zu ermitteln.

Wichtige Antwortfelder (Liste), je Eintrag:

- `slug` - Kürzel für den Pfad von `/weather/complete/{ort}`.
- `name` - Anzeigename.
- `region` - Bundesland bzw. Region.
- `lat`, `lon` - Koordinaten.

Beispiel-Aufruf:

```bash
curl http://localhost:6169/api/v1/weather/orte
```

Beispiel-Antwort (gekürzt):

```json
{
  "data": [
    { "slug": "koeln", "name": "Köln", "region": "Sachsen-Anhalt", "lat": 51.05, "lon": 12.14 },
    { "slug": "frankfurt", "name": "Frankfurt", "region": "Sachsen", "lat": 51.34, "lon": 12.37 }
  ],
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

---

## Layouts (Dashboard-Anordnungen)

Ein Layout ist eine benannte Kachel-Anordnung des Dashboards. Die Anordnung
selbst steckt in `daten`: eine Liste von Kacheln, je mit einer Kachel-ID und
ihrer Position bzw. Größe im Raster (`x`, `y`, `w`, `h`). Ein Layout kann als
Standard markiert sein (`ist_standard`).

Aufbau eines Layout-Objekts:

- `id` - eindeutige Kennung (UUID, vom Backend vergeben).
- `name` - Anzeigename des Layouts.
- `ist_standard` - `true`, wenn dies das Standard-Layout ist.
- `daten` - Liste von Kacheln, je `{ id, x, y, w, h }` (Rasterposition und
  -größe; `id` benennt die Kachelart, z. B. `aktuell`, `stunden`, `tage`).

### GET /layouts

Liste aller Layouts, sortiert nach Standard zuerst, dann nach Name. Ohne
Parameter.

Beispiel-Aufruf:

```bash
curl http://localhost:6169/api/v1/layouts
```

Beispiel-Antwort (gekürzt):

```json
{
  "data": [
    {
      "id": "b89ec8c7-80fb-4d93-b400-e98b5084454e",
      "name": "Zuhause",
      "ist_standard": true,
      "daten": [
        { "id": "aktuell", "x": 0, "y": 0, "w": 4, "h": 4 },
        { "id": "stunden", "x": 4, "y": 0, "w": 8, "h": 2 }
      ]
    }
  ],
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

### POST /layouts

Legt ein neues Layout an. Der Rumpf (JSON) darf folgende Felder enthalten, alle
optional:

- `name` - Anzeigename. Fehlt er, wird `"Neues Layout"` verwendet.
- `daten` - Kachel-Liste (siehe oben). Fehlt sie, wird eine leere Liste
  gespeichert.
- `ist_standard` - beim Anlegen ohne Wirkung; ein neues Layout ist zunächst kein
  Standard. Zum Markieren als Standard anschließend `PUT` verwenden.

Antwort: das neu angelegte Layout inklusive vergebener `id`.

Beispiel-Aufruf:

```bash
curl -X POST http://localhost:6169/api/v1/layouts \
  -H "Content-Type: application/json" \
  -d '{"name": "Balkon", "daten": [{"id": "aktuell", "x": 0, "y": 0, "w": 4, "h": 4}]}'
```

Beispiel-Antwort:

```json
{
  "data": {
    "id": "3f2c1a9e-0b44-4d2a-9c11-7e5d8a6b1234",
    "name": "Balkon",
    "ist_standard": false,
    "daten": [ { "id": "aktuell", "x": 0, "y": 0, "w": 4, "h": 4 } ]
  },
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

### PUT /layouts/{layout_id}

Aktualisiert ein vorhandenes Layout. Es werden nur die Felder geändert, die im
Rumpf angegeben sind (Teilaktualisierung); weggelassene Felder bleiben
unverändert.

Pfadparameter:

- `layout_id` - UUID des Layouts. Ist sie unbekannt, kommt `404`.

Rumpf (JSON), alle Felder optional: `name`, `daten`, `ist_standard`.

Antwort: das aktualisierte Layout.

Beispiel-Aufruf:

```bash
curl -X PUT http://localhost:6169/api/v1/layouts/3f2c1a9e-0b44-4d2a-9c11-7e5d8a6b1234 \
  -H "Content-Type: application/json" \
  -d '{"name": "Balkon Sommer", "ist_standard": true}'
```

Beispiel-Antwort:

```json
{
  "data": {
    "id": "3f2c1a9e-0b44-4d2a-9c11-7e5d8a6b1234",
    "name": "Balkon Sommer",
    "ist_standard": true,
    "daten": [ { "id": "aktuell", "x": 0, "y": 0, "w": 4, "h": 4 } ]
  },
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

### DELETE /layouts/{layout_id}

Löscht ein Layout. Der Aufruf ist idempotent: Er meldet auch dann Erfolg, wenn
die ID nicht (mehr) existiert.

Pfadparameter:

- `layout_id` - UUID des Layouts.

Antwort:

```json
{ "data": { "geloescht": true }, "meta": { "version": "0.1.0", "platzhalter": false } }
```

Beispiel-Aufruf:

```bash
curl -X DELETE http://localhost:6169/api/v1/layouts/3f2c1a9e-0b44-4d2a-9c11-7e5d8a6b1234
```

---

## GET /archiv/verlauf

Liefert den Tagesmittelwert einer Messgröße über einen Zeitraum aus dem eigenen
Langzeit-Archiv (PostgreSQL). Grundlage für die Verlaufskachel.

Abfrageparameter:

- `ort` - Ortskürzel (Slug), Standard `koeln`.
- `variable` - Messgröße. Aufgezeichnet werden `temperatur`, `feuchte`, `wind`
  und `druck`. Standard `temperatur`. Zur Erst-Befüllung wird nur `temperatur`
  rückwirkend für 30 Tage geladen; die übrigen Größen füllen sich ab
  Inbetriebnahme.
- `tage` - Anzahl der Tage rückwärts ab heute, Standard `30`.

Wichtige Antwortfelder (Liste, chronologisch aufsteigend), je Eintrag:

- `tag` - Datum als `"JJJJ-MM-TT"`.
- `wert` - Tagesmittel der gewählten Messgröße, auf eine Nachkommastelle
  gerundet.

Liegen für den Zeitraum keine Aufzeichnungen vor (z. B. unbekannter Ort oder
noch nicht befüllte Größe), ist die Liste leer.

Beispiel-Aufruf:

```bash
curl "http://localhost:6169/api/v1/archiv/verlauf?ort=koeln&variable=temperatur&tage=30"
```

Beispiel-Antwort (gekürzt):

```json
{
  "data": [
    { "tag": "2026-07-28", "wert": 19.3 },
    { "tag": "2026-07-29", "wert": 24.1 },
    { "tag": "2026-07-30", "wert": 26.4 }
  ],
  "meta": { "version": "0.1.0", "platzhalter": false }
}
```

---

## Grenzen, Aktualisierung und Frische

- Wetterdaten (`/weather/complete/{ort}`) werden serverseitig 10 Minuten
  zwischengespeichert. Innerhalb dieser Zeit liefern wiederholte Aufrufe die
  gleichen Werte; ein Live-Ticker im Minutentakt ist damit nicht sinnvoll.
- Die Grunddaten (aktueller Zustand, Stunden, Tage) stammen aus einem Wetterdienst
  mit für Deutschland hinterlegten Modellen; die konkrete Quelle ist hinter dem
  Backend gekapselt und austauschbar, ohne dass sich die Antwortform ändert.
- Die verfügbaren Orte sind derzeit fest hinterlegt (Köln, Frankfurt, Berlin,
  Hamburg, München). Neue Orte kommen zunächst nur durch eine
  Backend-Erweiterung hinzu.
- Das Archiv wird von einem Hintergrundprozess gefüllt: einmalig rückwirkend die
  stündliche Temperatur der letzten 30 Tage, danach fortlaufend alle 10 Minuten
  die aktuellen Werte (Temperatur, Feuchte, Wind, Druck). Der Verlauf reicht
  also frühestens 30 Tage zurück und wächst mit der Laufzeit; sehr frische Tage
  können noch wenige Messpunkte enthalten.
- Live-Blitze stammen aus einem Dienst im lokalen Netz und stehen außerhalb
  dieses Netzes in der Regel nicht zur Verfügung (`blitze` ist dann `null`).
- Es gibt keine Zugriffsbeschränkung (kein Schlüssel, keine Ratenbegrenzung); die
  Schnittstelle ist für den Eigenbetrieb gedacht.

## Nutzung in der Wetterwarte

- `GET /weather/complete/{ort}` ist die zentrale Quelle des Dashboards. Die
  Kacheln greifen jeweils auf einen Teilbereich der einen Antwort zu: `aktuell`,
  `stunden`, `tage`, `sonne` (Kachel Sonne/Mond), `nowcast`, `warnungen`, `luft`
  (Luftqualität) und `blitze`. Weil alles in einem Aufruf kommt, genügt ein
  Datenabruf je Ort und Aktualisierung.
- `GET /weather/orte` füllt die Ortsauswahl und liefert die gültigen Slugs für
  den Complete-Aufruf.
- Die Layout-Endpunkte sichern die vom Benutzer im Raster angeordneten Kacheln.
  Das als Standard markierte Layout wird beim Start geladen. Beim Verschieben
  oder Ändern der Kacheln schreibt das Frontend die neue Anordnung per `PUT`
  zurück; die `daten`-Liste entspricht der Rastergröße und -position je Kachel.
- `GET /archiv/verlauf` speist die Verlaufskachel (Langzeit-Trend). Wähle `ort`
  passend zum angezeigten Ort, `variable` passend zur Kachel und `tage` passend
  zum gewünschten Zeitfenster.
- Prüfe in der Auswertung stets `meta.platzhalter` sowie die Felder, die `null`
  sein können (`luft`, `nowcast`, `blitze`, einzelne Werte wie `sicht`), damit
  die Kacheln bei fehlenden Zusatzdaten sauber leer bleiben statt Fehler zu
  zeigen.
