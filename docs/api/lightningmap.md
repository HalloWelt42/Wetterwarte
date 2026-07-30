# lightningmap - Live-Blitze

Der lightningmap-Dienst läuft lokal auf dem Pi und liefert weltweite Blitzeinschläge nahezu in Echtzeit sowie ein Tagesarchiv. Zusätzlich stellt er einen zwischengespeicherten Karten-Kachel-Proxy bereit, damit die Karte im LAN ohne direkten Zugriff auf fremde Kachel-Server dargestellt werden kann.

## Basis-URL

```
http://192.168.178.49:8100
```

Alle Datenendpunkte liegen unter dem Präfix `/api`. Der Dienst ist nur im lokalen Netz erreichbar, benötigt keine Authentifizierung und antwortet mit JSON (Ausnahme: der Kachel-Proxy liefert PNG-Bilder).

## Datenquelle

Die Rohdaten stammen von Blitzortung.org und werden über MQTT bezogen. Der Pi ist als Dauerabnehmer mit dem MQTT-Proxy verbunden, wandelt die Meldungen in ein schlankes Format um und hält sie in einem Ringpuffer im Arbeitsspeicher sowie in Tagesdateien auf der Platte vor.

Details liefert der Endpunkt `/api/source` (siehe unten). Feste Eckdaten der Quelle:

- Typ: MQTT
- Host: `blitzortung.ha.sed.pl`, Port `1883`
- Thema (Topic): `blitzortung/1.1/#`

## Gemeinsames Datenmodell eines Blitzes

Sowohl die Live- als auch die Archiv-Abfrage liefern Blitze als kompakte Objekte mit vier Feldern:

| Feld  | Typ      | Bedeutung |
|-------|----------|-----------|
| `t`   | Zahl     | Zeitpunkt des Einschlags als Unix-Zeit in **Millisekunden** (UTC). Beispiel: `1785369584246` entspricht `2026-07-29T23:59:44Z`. |
| `lat` | Zahl     | Geografische Breite in Grad (-90 bis 90). |
| `lon` | Zahl     | Geografische Länge in Grad (-180 bis 180). |
| `sta` | Ganzzahl | Stations- bzw. Statuskennung des Einschlags. In den gelieferten Daten steht dieses Feld durchgängig auf `0`; die Wetterwarte wertet es nicht aus. |

## Endpunkte

### GET /api/strikes - aktuelle Blitze im Ausschnitt

Liefert alle bekannten Blitze innerhalb eines rechteckigen Kartenausschnitts (Bounding-Box) aus dem Live-Puffer der letzten Stunden.

**Parameter**

| Name    | Pflicht | Typ      | Bereich / Standard | Beschreibung |
|---------|---------|----------|--------------------|--------------|
| `north` | ja      | Zahl     | -90 bis 90         | Nordrand der Box (Breite). |
| `south` | ja      | Zahl     | -90 bis 90         | Südrand der Box (Breite). |
| `east`  | ja      | Zahl     | -180 bis 180       | Ostrand der Box (Länge). |
| `west`  | ja      | Zahl     | -180 bis 180       | Westrand der Box (Länge). |
| `since` | nein    | Zahl     | 0.1 bis 24, Standard 2 | Zeitfenster in **Stunden** rückwärts ab jetzt. |
| `limit` | nein    | Ganzzahl | 1 bis 100000, Standard 50000 | Maximale Anzahl zurückgegebener Blitze. |

Fehlt eine der vier Box-Grenzen, antwortet der Dienst mit HTTP 422 und einer Feldliste. Ein `since` größer als 24 wird ebenfalls mit HTTP 422 abgelehnt.

**Wichtige Antwortfelder**

- `strikes`: Liste der Blitze (Modell siehe oben), neueste nicht zwingend zuerst.
- `count`: Anzahl der zurückgegebenen Blitze.
- `bounds`: die tatsächlich verwendete Box (`north`, `south`, `east`, `west`).
- `since_hours`: das angewandte Zeitfenster in Stunden.
- `source`: Herkunft der Daten, hier `live_buffer`.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/strikes?north=55&south=47&east=15&west=5&since=1&limit=500"
```

**Beispiel-Antwort (gekürzt)**

```json
{
  "strikes": [
    { "t": 1785369584246, "lat": 32.2335, "lon": -75.0266, "sta": 0 },
    { "t": 1785369585417, "lat": 23.2201, "lon": 134.8543, "sta": 0 }
  ],
  "count": 2,
  "bounds": { "north": 55.0, "south": 47.0, "east": 15.0, "west": 5.0 },
  "since_hours": 1.0,
  "source": "live_buffer"
}
```

### GET /api/strikes/history - Blitze eines vergangenen Tages

Wie `/api/strikes`, liefert die Daten aber aus den gespeicherten Tagesdateien statt aus dem Live-Puffer. Damit lassen sich zurückliegende Tage nachschlagen.

**Parameter**

| Name    | Pflicht | Typ      | Bereich / Standard | Beschreibung |
|---------|---------|----------|--------------------|--------------|
| `date`  | ja      | Text     | Format `JJJJ-MM-TT` | Der abzufragende Tag, zum Beispiel `2026-07-29`. |
| `north` | ja      | Zahl     | -90 bis 90         | Nordrand der Box. |
| `south` | ja      | Zahl     | -90 bis 90         | Südrand der Box. |
| `east`  | ja      | Zahl     | -180 bis 180       | Ostrand der Box. |
| `west`  | ja      | Zahl     | -180 bis 180       | Westrand der Box. |
| `limit` | nein    | Ganzzahl | 1 bis 100000, Standard 50000 | Maximale Anzahl. |

Ein Zeitfenster (`since`) gibt es hier nicht, da der ganze Tag betrachtet wird. Welche Tage verfügbar sind, verrät `/api/strikes/dates`.

**Wichtige Antwortfelder**

- `date`: der ausgelieferte Tag.
- `strikes`, `count`, `bounds`: wie bei `/api/strikes`.
- `source`: hier `history_files`.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/strikes/history?date=2026-07-29&north=55&south=47&east=15&west=5&limit=500"
```

**Beispiel-Antwort (gekürzt)**

```json
{
  "date": "2026-07-29",
  "strikes": [
    { "t": 1785342528332, "lat": -9.0797, "lon": 155.9352, "sta": 0 }
  ],
  "count": 1,
  "bounds": { "north": 55.0, "south": 47.0, "east": 15.0, "west": 5.0 },
  "source": "history_files"
}
```

### GET /api/strikes/dates - verfügbare Archiv-Tage

Liefert die Liste aller Tage, für die Archivdaten vorliegen. Ohne Parameter. Praktisch, um vor einer History-Abfrage zu prüfen, welche Daten es gibt.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/strikes/dates"
```

**Beispiel-Antwort (gekürzt)**

```json
{ "dates": ["2026-07-29", "2026-07-28", "2026-07-27"] }
```

Die Tage sind absteigend sortiert (neuester zuerst).

### GET /api/stats - Betriebszahlen

Liefert Kennzahlen zu Speicher, MQTT-Verbindung und aktiven WebSocket-Clients. Ohne Parameter. Gut geeignet für eine Zustandsanzeige oder zur Fehlersuche.

**Wichtige Antwortfelder**

- `storage.live.count`: aktuell im Puffer gehaltene Blitze.
- `storage.live.max_capacity`: maximale Puffergröße (Ringpuffer).
- `storage.live.strikes_per_minute`: aktuelle Zulaufrate.
- `storage.history.total_files` / `total_size_mb`: Umfang des Tagesarchivs.
- `mqtt.connected`: ob die Verbindung zur Quelle gerade steht.
- `mqtt.last_strike`: Zeitstempel des zuletzt empfangenen Blitzes.
- `mqtt.reconnect_count`: Anzahl der bisherigen Wiederverbindungen (Hinweis auf Instabilität).
- `websocket_clients`: Zahl der gerade verbundenen Live-Abnehmer.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/stats"
```

**Beispiel-Antwort (gekürzt)**

```json
{
  "storage": {
    "live": { "count": 82591, "total_received": 7486284, "strikes_per_minute": 330, "max_capacity": 100000 },
    "history": { "geohash_regions": 566, "total_files": 32973, "total_size_mb": 3134.7, "total_written": 7486284, "buffer_size": 0 }
  },
  "mqtt": {
    "connected": false, "host": "blitzortung.ha.sed.pl", "port": 1883,
    "topic": "blitzortung/1.1/#", "uptime_seconds": 80579, "reconnect_count": 24,
    "last_strike": "2026-07-30T00:00:06.428597", "parse_errors": 0,
    "strikes_received": 7486284, "strikes_per_minute": 330
  },
  "websocket_clients": 0
}
```

### GET /api/source - Beschreibung der Datenquelle

Liefert die statischen Eckdaten der MQTT-Quelle. Ohne Parameter.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/source"
```

**Beispiel-Antwort**

```json
{
  "type": "MQTT",
  "host": "blitzortung.ha.sed.pl",
  "port": 1883,
  "topic": "blitzortung/1.1/#",
  "description": "Blitzortung.org MQTT Proxy"
}
```

### WebSocket /ws - Live-Broadcast

Für Anzeigen, die neue Blitze sofort erhalten sollen, gibt es einen WebSocket unter `ws://192.168.178.49:8100/ws`. Der Server sendet unmittelbar nach dem Verbindungsaufbau eine Begrüßungsnachricht und danach fortlaufend neu eintreffende Blitze an alle verbundenen Clients. Anders als die HTTP-Endpunkte filtert der Broadcast nicht nach Ausschnitt; die Auswahl des relevanten Bereichs übernimmt der Client.

**Begrüßungsnachricht (direkt nach Verbindung)**

```json
{ "type": "connected", "version": "2.20.7", "mqtt_connected": false, "live_strikes": 81803 }
```

- `type`: `connected` kennzeichnet die Erstnachricht.
- `version`: Version des lightningmap-Dienstes.
- `mqtt_connected`: ob die Quelle gerade Daten liefert.
- `live_strikes`: aktuelle Puffergröße zum Zeitpunkt der Verbindung.

Danach folgen Nachrichten mit neuen Blitzen. Deren Nutzdaten entsprechen dem oben beschriebenen Blitz-Modell (`t`, `lat`, `lon`, `sta`). Solange `mqtt_connected` `false` ist (Quelle in Wiederverbindung), kommen keine neuen Blitze; die HTTP-Endpunkte liefern in dieser Zeit weiterhin Puffer- und Archivdaten.

Hinweis: Nur der Pfad `/ws` handelt das WebSocket-Protokoll aus (HTTP 101). Andere Pfade lehnen den Upgrade ab.

### GET /api/tile/{provider}/{z}/{x}/{y} - zwischengespeicherter Karten-Kachel-Proxy

Liefert eine einzelne Karten-Kachel als PNG. Der Pi holt die Kachel bei Bedarf einmalig vom jeweiligen Anbieter, legt sie im lokalen Cache ab und bedient danach alle Anfragen direkt aus dem Cache. So bleibt die Kartendarstellung auch ohne freien Zugriff auf externe Kachel-Server schnell und funktionsfähig.

**Pfadparameter**

| Name       | Typ      | Beschreibung |
|------------|----------|--------------|
| `provider` | Text     | Kartenstil (siehe Tabelle unten). |
| `z`        | Ganzzahl | Zoomstufe. |
| `x`        | Ganzzahl | Kachel-Spalte. |
| `y`        | Ganzzahl | Kachel-Zeile. Ohne Dateiendung angeben (also `.../4/2`, nicht `.../4/2.png`). |

**Verfügbare Stile (`provider`)**

`dark`, `dark-labels`, `light`, `voyager`, `satellite`, `satellite-labels`.

Ein unbekannter Stil führt zu HTTP 404.

**Antwort**

Bei Erfolg HTTP 200 mit `Content-Type: image/png`. Der Header `X-Tile-Cache` zeigt `hit` (aus dem Cache) oder `miss` (frisch geladen) an. Der Cache-Header erlaubt langes clientseitiges Zwischenspeichern (`Cache-Control: public, max-age=2592000, immutable`, also rund 30 Tage).

**Beispiel-Aufruf**

```bash
curl -o kachel.png "http://192.168.178.49:8100/api/tile/voyager/3/4/2"
```

**Beispiel-Antwort (Header-Auszug)**

```
HTTP/1.1 200 OK
content-type: image/png
cache-control: public, max-age=2592000, immutable
x-tile-cache: hit
content-length: 16155
```

### GET /api/tile/_status - Zustand des Kachel-Caches

Liefert je Stil die Anzahl und Größe der gespeicherten Kacheln sowie eine globale Trefferstatistik. Ohne Parameter.

**Beispiel-Aufruf**

```bash
curl "http://192.168.178.49:8100/api/tile/_status"
```

**Beispiel-Antwort (gekürzt)**

```json
{
  "providers": {
    "voyager": { "tiles": 3031, "size_bytes": 17281578 },
    "satellite": { "tiles": 10508, "size_bytes": 147648696 }
  },
  "global": { "hits": 386, "misses": 0, "errors": 0, "bytes_served": 5874338, "uptime_s": 1000339 }
}
```

## Grenzen, Aktualisierung und Frische

- **Live-Puffer**: Der Ringpuffer fasst maximal 100000 Blitze (`storage.live.max_capacity`). Bei hoher Aktivität (beobachtet rund 330 Blitze pro Minute) deckt er entsprechend nur wenige Stunden ab; ältere Blitze fallen heraus. Das Zeitfenster `since` ist auf maximal 24 Stunden begrenzt.
- **Obergrenze pro Abfrage**: `limit` reicht bis 100000, Standard ist 50000. Große Ausschnitte oder lange Zeitfenster können viele Punkte liefern; für eine Kachel-Ansicht genügt ein enger Ausschnitt mit kleinem `limit`.
- **Archiv**: Vergangene Tage stehen als Tagesdateien bereit (im Beispielstand über 30000 Dateien, rund 3 GB). Die abfragbaren Tage listet `/api/strikes/dates`; sie reichten im Test mehrere Wochen zurück.
- **Frische der Live-Daten**: Neue Blitze treffen nur ein, solange die MQTT-Verbindung steht (`mqtt.connected` bzw. `mqtt_connected`). Die Verbindung kann sich zeitweise trennen und neu aufbauen (im Test war `connected` vorübergehend `false` bei bereits 24 Wiederverbindungen). In solchen Phasen liefern Puffer und Archiv weiter, es kommen aber keine frischen Einschläge und keine WebSocket-Broadcasts. Der Zeitstempel `mqtt.last_strike` und die Rate `strikes_per_minute` aus `/api/stats` zeigen, ob gerade Daten fließen.
- **Kachel-Cache**: Kacheln gelten als unveränderlich und werden lange vorgehalten (30 Tage `max-age`). Neue Ausschnitte werden beim ersten Zugriff nachgeladen (`X-Tile-Cache: miss`).

## Nutzung in der Wetterwarte

Die Blitz-Kachel der Wetterwarte spricht diesen Dienst über den Client `backend/src/wetterwarte/providers/blitze.py` an. Die Basis-URL steht in `config.py` als `lightning_base` (Standard `http://192.168.178.49:8100`).

- **Abfrage**: Die Kachel ruft `GET /api/strikes` mit einer Box rund um den gewählten Ort auf (etwa plus/minus 1.3 Grad Breite und plus/minus 2.08 Grad Länge) und `limit=500`.
- **Auswertung**: Aus der Antwort zählt sie die Blitze der letzten Stunde (`anzahl`) und bildet für die drei jüngsten Einschläge je einen Eintrag mit Alter (`vor X Min`), Entfernung in Kilometern (Haversine) und Himmelsrichtung.
- **LAN-Direktzugriff**: Der Client nutzt bewusst `trust_env=False`, damit die Anfrage an den lokalen Pi nicht über einen Proxy umgeleitet wird.
- **Kartenhintergrund**: Für die Kartendarstellung der Kachel dient der Kachel-Proxy `/api/tile/{provider}/{z}/{x}/{y}`, sodass die Karte offline-tauglich aus dem lokalen Cache kommt.
- Das Feld `sta` wird derzeit nicht ausgewertet.
