# OSMLocal - selbst gehosteter OSM-Kartenserver

## Zweck

OSMLocal liefert Vektorkacheln, Kartenstile, Schriften, Symbole und eine Ortssuche für Deutschland vollständig aus dem eigenen Netz (Raspberry Pi). Damit zeigt die Wetterwarte eine schnelle, datensparsame Basiskarte an, ohne einen fremden Kartendienst aufzurufen.

## Basis-URL

- API (Backend): `http://192.168.178.49:8120/api/v1`
- Weboberfläche (Frontend): `http://192.168.178.49:8121`
- Gesundheitscheck: `http://192.168.178.49:8120/health`
- Maschinenlesbare Schnittstellenbeschreibung: `http://192.168.178.49:8120/openapi.json`

Alle im Folgenden gezeigten Pfade hängen an der API-Basis-URL. Der Server antwortet mit JSON, mit binären Kacheln (Protobuf) oder mit Bildern (PNG), je nach Endpunkt.

## Region und Grenzen

- Abdeckung: nur Deutschland (ungefähre Bounding-Box `5.864417, 47.26543` bis `15.05078, 55.14777`, Mittelpunkt etwa `10.46, 51.21`).
- Zoomstufen: 0 bis 14. Höhere Zoomstufen liefern keine Daten (siehe Abschnitt "Grenzen").
- Kachelschema: `shortbread` (VersaTiles-Datensatz), Kachelraster `xyz` (Ursprung oben links).
- Herkunft und Namensnennung der Daten: OpenStreetMap-Mitwirkende. Die Namensnennung ist im Stil bereits hinterlegt und wird von der Karte automatisch angezeigt.

---

## Endpunkte

### 1. Kartenstil abrufen

`GET /style/{style_id}.json`

Liefert einen vollständigen MapLibre-Stil (Style-Spezifikation Version 8). Der Stil enthält bereits absolute URLs zu Schriften (`glyphs`), Symbolen (`sprite`) und Vektorkacheln (`sources`), die alle auf denselben Server zeigen. Für die Wetterwarte ist dies der wichtigste Einstiegspunkt: eine einzige URL genügt, um die komplette Karte zu laden.

Verfügbare Stil-IDs:

- `colorful` - heller Farbstil ("Farbig")
- `eclipse` - dunkler Stil ("Dunkel")

Parameter:

- `style_id` (Pfad, Pflicht): `colorful` oder `eclipse`. Unbekannte IDs liefern HTTP 404.

Wichtige Antwortfelder:

- `version` - immer `8` (MapLibre-Style-Version).
- `glyphs` - URL-Vorlage für Schriften mit Platzhaltern `{fontstack}` und `{range}`.
- `sprite` - Liste mit Symbolsatz (Feld `url` zeigt auf den Sprite-Endpunkt).
- `sources` - Datenquelle `versatiles-shortbread` mit `tiles` (Kachel-URL inklusive Cache-Version `?v=...`), `attribution`, `minzoom`, `maxzoom`.
- `layers` - alle Zeichenebenen (Hintergrund, Wasser, Straßen, Beschriftungen und so weiter).

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/style/colorful.json"
```

Beispiel-Antwort (gekürzt):

```json
{
  "version": 8,
  "name": "versatiles-colorful",
  "metadata": { "license": "https://creativecommons.org/publicdomain/zero/1.0/" },
  "glyphs": "http://192.168.178.49:8120/api/v1/glyphs/{fontstack}/{range}.pbf",
  "sprite": [ { "id": "basics", "url": "http://192.168.178.49:8120/api/v1/sprites/sprites" } ],
  "sources": {
    "versatiles-shortbread": {
      "type": "vector",
      "tiles": ["http://192.168.178.49:8120/api/v1/tiles/germany/{z}/{x}/{y}.pbf?v=1785120002"],
      "attribution": "(c) OpenStreetMap contributors",
      "minzoom": 0,
      "maxzoom": 14
    }
  },
  "layers": [ { "id": "background", "type": "background", "paint": { "background-color": "rgb(249,244,238)" } } ]
}
```

---

### 2. Verfügbare Stile auflisten

`GET /styles`

Liefert die Liste aller Stile. Praktisch, um in der Oberfläche eine Umschaltung zwischen hell und dunkel anzubieten.

Wichtige Antwortfelder je Eintrag:

- `id` - technische Kennung für den Stil-Endpunkt.
- `name` - Anzeigename (deutsch).
- `dark` - `true`, wenn es ein dunkler Stil ist.

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/styles"
```

Beispiel-Antwort:

```json
[
  { "id": "colorful", "name": "Farbig", "dark": false },
  { "id": "eclipse",  "name": "Dunkel", "dark": true }
]
```

---

### 3. Vektorkacheln abrufen

`GET /tiles/{tileset}/{z}/{x}/{y}.pbf`

Liefert eine Vektorkachel im Mapbox-Vector-Tile-Format (Protobuf). Die Antwort ist gzip-komprimiert (`content-encoding: gzip`); MapLibre entpackt sie selbst. Diesen Endpunkt ruft die Karte im Normalfall nicht direkt auf, sondern über die im Stil hinterlegte URL-Vorlage.

Parameter:

- `tileset` (Pfad, Pflicht): derzeit nur `germany`.
- `z` (Pfad, Pflicht): Zoomstufe 0 bis 14.
- `x`, `y` (Pfad, Pflicht): Kachelkoordinaten im xyz-Raster.

Verhalten:

- Vorhandene Kachel: HTTP 200, `content-type: application/x-protobuf`, `content-encoding: gzip`.
- Kachel außerhalb des Zoombereichs oder ohne Inhalt: HTTP 204 (kein Inhalt).
- Antworten tragen `cache-control: public, max-age=31536000, immutable`, sind also aggressiv zwischenspeicherbar. Der Parameter `?v=...` im Stil sorgt bei neuen Daten für frische URLs.

Beispiel-Aufruf:

```bash
curl -D - -o kachel.pbf \
  "http://192.168.178.49:8120/api/v1/tiles/germany/6/33/21.pbf"
```

Beispiel-Antwort (nur Kopfzeilen, der Rumpf ist Binärdaten):

```
HTTP/1.1 200 OK
cache-control: public, max-age=31536000, immutable
content-encoding: gzip
content-type: application/x-protobuf
content-length: 192573
```

---

### 4. TileJSON abrufen

`GET /tilejson/{tileset}.json`

Liefert eine TileJSON-Beschreibung (Version 3.0.0) des Kachelsatzes: Kachel-URL-Vorlage, Zoombereich, Bounding-Box, Mittelpunkt und die Liste aller Vektorebenen mit ihren Attributfeldern. Nützlich, wenn eine Quelle in MapLibre ohne kompletten Stil eingebunden werden soll, oder um zu prüfen, welche Ebenen und Felder verfügbar sind.

Hinweis: Die `tiles`-URL im TileJSON ist relativ (`/api/v1/tiles/...`), enthält also keinen Host. Für die Wetterwarte ist der Stil-Endpunkt (Abschnitt 1) meist bequemer, weil dort absolute URLs stehen.

Parameter:

- `tileset` (Pfad, Pflicht): derzeit nur `germany`. Unbekannte Namen liefern HTTP 404.

Wichtige Antwortfelder:

- `tiles` - URL-Vorlage der Kacheln.
- `minzoom`, `maxzoom` - `0` und `14`.
- `bounds`, `center` - Bounding-Box und Startmittelpunkt für Deutschland.
- `vector_layers` - alle Ebenen (zum Beispiel `place_labels`, `boundaries`, `streets`, `buildings`, `water_polygons`, `pois`) samt `fields` und ebenenspezifischem Zoombereich.

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/tilejson/germany.json"
```

Beispiel-Antwort (gekürzt):

```json
{
  "tilejson": "3.0.0",
  "name": "germany",
  "scheme": "xyz",
  "tiles": ["/api/v1/tiles/germany/{z}/{x}/{y}.pbf"],
  "minzoom": 0,
  "maxzoom": 14,
  "bounds": [5.864417, 47.26543, 15.05078, 55.14777],
  "center": [10.4575985, 51.2066, 7],
  "vector_layers": [
    { "id": "place_labels", "fields": { "kind": "String", "name": "String", "population": "Number" }, "minzoom": 3, "maxzoom": 14 }
  ]
}
```

---

### 5. Rasterkacheln abrufen (PNG)

`GET /raster/{style}/{z}/{x}/{y}.png`

Liefert eine serverseitig gerenderte PNG-Kachel für einen Stil. Sinnvoll als Rückfalllösung für Umgebungen ohne Vektorunterstützung oder für einfache Bildvorschauen. Für die interaktive Karte der Wetterwarte sind die Vektorkacheln (Abschnitt 3) die erste Wahl, weil sie schärfer skalieren und den Stil clientseitig anwenden.

Parameter:

- `style` (Pfad, Pflicht): `colorful` oder `eclipse`.
- `z` (Pfad, Pflicht): Zoomstufe 0 bis 14.
- `x`, `y` (Pfad, Pflicht): Kachelkoordinaten im xyz-Raster.

Antwort: HTTP 200, `content-type: image/png`, ebenfalls langfristig zwischenspeicherbar.

Beispiel-Aufruf:

```bash
curl -o kachel.png \
  "http://192.168.178.49:8120/api/v1/raster/colorful/6/33/21.png"
```

Beispiel-Antwort (nur Kopfzeilen, der Rumpf ist ein PNG-Bild):

```
HTTP/1.1 200 OK
content-type: image/png
content-length: 13516
cache-control: public, max-age=31536000, immutable
```

---

### 6. Schriften (Glyphs) abrufen

`GET /glyphs/{fontstack}/{range_name}.pbf`

Liefert Schriftglyphen als Protobuf, wie sie MapLibre zum Beschriften der Karte braucht. Dieser Endpunkt wird über die `glyphs`-Vorlage im Stil automatisch angesprochen; ein direkter Aufruf ist selten nötig.

Parameter:

- `fontstack` (Pfad, Pflicht): Name der Schrift, zum Beispiel `noto_sans_regular` oder `noto_sans_bold`. Mehrere Schriften lassen sich mit Komma kombinieren (`noto_sans_regular,noto_sans_bold`).
- `range_name` (Pfad, Pflicht): Zeichenbereich in 256er-Blöcken, zum Beispiel `0-255`, `256-511`.

Antwort: HTTP 200, `content-type: application/x-protobuf`, mit `etag` und `last-modified` für Zwischenspeicherung.

Beispiel-Aufruf:

```bash
curl -D - -o glyphs.pbf \
  "http://192.168.178.49:8120/api/v1/glyphs/noto_sans_regular/0-255.pbf"
```

Beispiel-Antwort (nur Kopfzeilen, der Rumpf ist Binärdaten):

```
HTTP/1.1 200 OK
content-type: application/x-protobuf
content-length: 83533
etag: "f331c77afbf6ad14b7a2bcfc5f063b28"
```

---

### 7. Symbole (Sprites) abrufen

`GET /sprites/{name}`

Liefert den Symbolsatz für Kartensymbole (Points of Interest, Verkehr und so weiter). Ein Sprite besteht aus zwei zusammengehörigen Dateien: einer JSON-Datei mit den Positionen und einer PNG-Datei mit dem Bild. Für hochauflösende Anzeigen gibt es zusätzlich die `@2x`-Varianten. Auch dieser Endpunkt wird über die `sprite`-Angabe im Stil automatisch geladen.

Übliche Namen:

- `sprites.json` - Positions- und Größenangaben je Symbol.
- `sprites.png` - das Sprite-Bild.
- `sprites@2x.json` und `sprites@2x.png` - Varianten für Bildschirme mit hoher Pixeldichte.

Wichtige Antwortfelder (in `sprites.json`) je Symbol:

- `width`, `height` - Größe in Pixeln.
- `x`, `y` - Position im Sprite-Bild.
- `pixelRatio` - Pixelverhältnis.
- `sdf` - `true`, wenn das Symbol als Signed-Distance-Field einfärbbar ist.

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/sprites/sprites.json"
```

Beispiel-Antwort (gekürzt):

```json
{
  "icon-airfield": { "width": 32, "height": 32, "x": 0,  "y": 0,  "pixelRatio": 1, "sdf": true },
  "icon-airport":  { "width": 32, "height": 32, "x": 32, "y": 0,  "pixelRatio": 1, "sdf": true }
}
```

---

### 8. Ortssuche (Vorwärtssuche)

`GET /suche?q={text}`

Sucht Orte, Straßen und Points of Interest anhand eines Textes und gibt passende Treffer mit Koordinaten zurück. Grundlage für eine Ortseingabe in der Wetterwarte, etwa um einen Standort auf der Karte zu setzen.

Parameter:

- `q` (Abfrage, Pflicht): Suchtext, zum Beispiel `Berlin` oder `Hauptbahnhof`.
- `limit` (Abfrage, optional): maximale Trefferzahl (Standard liefert bis zu 8 Treffer).
- `nahe` (Abfrage, optional): Vorzugspunkt im Format `lng,lat` (Länge zuerst, dann Breite; Reihenfolge wie beim Umkehr-Endpunkt und wie in GeoJSON). Treffer in der Nähe dieses Punkts werden bevorzugt. Beispiel: `nahe=9.99,53.55` bevorzugt Ergebnisse rund um Hamburg.

Wichtige Antwortfelder:

- `query` - der ausgewertete Suchtext.
- `count` - Anzahl der Treffer.
- `results` - Liste der Treffer, je Treffer:
  - `name` - Bezeichnung des Orts.
  - `kind` - genauer Typ, zum Beispiel `city`, `village`, `residential`, `bus_stop`, `shop:bakery`.
  - `category` - grobe Kategorie: `ort`, `strasse` oder `poi`.
  - `lng`, `lat` - Länge und Breite (Dezimalgrad).
  - `bbox` - Bounding-Box, falls vorhanden (sonst `null`).
  - `context` - Zusatzkontext, falls vorhanden (sonst `null`).

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/suche?q=Buxtehude&limit=3"
```

Beispiel-Antwort (gekürzt):

```json
{
  "query": "Buxtehude",
  "count": 3,
  "results": [
    { "name": "Buxtehude", "kind": "town", "category": "ort", "lng": 9.7003941, "lat": 53.4767351, "bbox": null, "context": null },
    { "name": "Buxtehudeweg", "kind": "residential", "category": "strasse", "lng": 10.6563903, "lat": 53.8697904, "bbox": null, "context": null }
  ]
}
```

---

### 9. Umkehrsuche (Koordinate zu Ort)

`GET /suche/umkehr?lng={lng}&lat={lat}`

Wandelt eine Koordinate in den nächstgelegenen Ort oder die nächstgelegene Straße um (Reverse Geocoding). Nützlich, um nach einem Klick auf die Karte einen lesbaren Standortnamen anzuzeigen.

Parameter:

- `lng` (Abfrage, Pflicht): geografische Länge in Dezimalgrad.
- `lat` (Abfrage, Pflicht): geografische Breite in Dezimalgrad.

Achtung: Beide Parameter sind Pflicht. Fehlt einer (oder heißt er abweichend, etwa `lon` statt `lng`), antwortet der Server mit HTTP 422 und einer Fehlermeldung.

Antwort: eine Liste von Treffern (gleiche Felder wie bei der Vorwärtssuche: `name`, `kind`, `category`, `lng`, `lat`, `bbox`, `context`). Der erste Eintrag ist in der Regel der beste Treffer.

Beispiel-Aufruf:

```bash
curl "http://192.168.178.49:8120/api/v1/suche/umkehr?lat=52.52&lng=13.405"
```

Beispiel-Antwort:

```json
[
  { "name": "Karl-Liebknecht-Straße", "kind": "primary", "category": "strasse", "lng": 13.4049874, "lat": 52.5200133, "bbox": null, "context": null }
]
```

---

## Grenzen, Aktualisierung und Frische

### Grenzen

- Nur Deutschland: Anfragen außerhalb der abgedeckten Fläche liefern keine Kacheln.
- Zoombereich 0 bis 14: Kacheln über Zoom 14 gibt es nicht; solche Anfragen liefern HTTP 204 (kein Inhalt).
- Unbekannte Stile oder Kachelsätze liefern HTTP 404.
- Adressen und Points of Interest erscheinen erst auf hohen Zoomstufen (Ebenen `addresses`, `buildings`, `pois` ab Zoom 14).

### Frische prüfen

Für Status und Frische stehen zusätzliche Lese-Endpunkte bereit:

- `GET /health` - schneller Gesundheitscheck. Beispiel: `{ "status": "healthy", "app": "OSMLocal", "version": "0.1.0", "daten_vorhanden": true }`.
- `GET /api/v1/status` - Gesamtstatus mit Version, Region, Datenumfang (`data.size_mb`), letztem Kachel-Build (`last_build` mit `status`, `started_at`, `finished_at`, `duration_s`), laufendem Build (`build_running`), Kachelsätzen, Stilen und der aktuellen Kachelversion (`tiles_version`).
- `GET /api/v1/daten/status` - kompakter Datenstatus (`available`, `size_mb`, `last_checked`, `next_update`).
- `GET /api/v1/tilesets` - Liste der Kachelsätze mit `min_zoom`, `max_zoom`, `size_mb` und `updated_at`.

Beispiel:

```bash
curl "http://192.168.178.49:8120/api/v1/daten/status"
```

```json
{ "available": true, "data_date": null, "sequence": null, "size_mb": 4546.3, "last_checked": "2026-07-29T01:00:00+00:00", "next_update": null }
```

### Aktualisierung

Die OSM-Daten und die daraus erzeugten Kacheln werden über die Weboberfläche (`http://192.168.178.49:8121`) gepflegt und periodisch neu erzeugt (der letzte Build dauerte etwa 50 Minuten). Bei einem neuen Build ändert sich die Kachelversion; der Stil hängt diese als `?v=...` an die Kachel-URL an, sodass Clients automatisch frische Kacheln laden, obwohl die Antworten selbst als `immutable` zwischengespeichert werden dürfen. Wer immer den aktuellen Stand braucht, lädt den Stil (Abschnitt 1) neu, weil dort die jeweils gültige Kachelversion eingebettet ist.

## Hinweise zur Nutzung in der Wetterwarte

- Basiskarte mit MapLibre: die Karte wird mit einer einzigen Stil-URL initialisiert, zum Beispiel `style: "http://192.168.178.49:8120/api/v1/style/colorful.json"`. Schriften, Symbole und Kacheln lädt MapLibre dann selbstständig, weil im Stil bereits absolute URLs zum Pi stehen.
- Hell und Dunkel: für einen Themenwechsel den Stil zwischen `colorful` (hell) und `eclipse` (dunkel) umschalten. Die Liste dafür liefert `/api/v1/styles`.
- Sinnvolle Kartengrenzen setzen: `maxZoom` auf 14 begrenzen und die Ansicht per `maxBounds` auf Deutschland beschränken, damit keine leeren Bereiche entstehen (Bounding-Box siehe TileJSON, Abschnitt 4).
- Ortssuche: die Standortauswahl der Wetterwarte kann `/api/v1/suche` für die Eingabe nutzen und `nahe=lng,lat` mit dem aktuellen Kartenmittelpunkt füttern, damit nahe Treffer oben stehen.
- Klick auf die Karte: mit `/api/v1/suche/umkehr` lässt sich zu einer angeklickten Koordinate ein lesbarer Ortsname anzeigen.
- Datensparsam und offline im eigenen Netz: alle Aufrufe bleiben im lokalen Netz, es wird kein externer Kartendienst kontaktiert. Die Namensnennung der OpenStreetMap-Mitwirkenden ist im Stil hinterlegt und muss in der Karte sichtbar bleiben.
- Raster als Rückfall: wo keine Vektorkarte möglich ist, liefert `/api/v1/raster/{style}/{z}/{x}/{y}.png` fertige Bildkacheln.
