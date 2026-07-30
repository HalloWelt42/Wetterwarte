# Voll selbst gehostet

Leitprinzip der Wetterwarte: ausser den reinen Wetter-Rohdaten laeuft alles lokal.
Dieses Dokument beschreibt den Weg zur vollstaendigen Unabhaengigkeit und den
aktuellen Stand.

## Was schon lokal laeuft

- Karten: eigener OSM-Kachelserver (osmlocal) auf dem Pi, eingebunden ueber den
  Vite-Proxy (`/karte`). Keine externen Kartenkacheln.
- Icons und Schrift: lokal gebuendelt (Meteocons, Font Awesome, Barlow), keine CDN.
- Blitze: eigener lightningmap-Dienst auf dem Pi.
- Datenbank und Cache: Postgres und Redis ausschliesslich als Docker-Container.
- Langzeit-Archiv: eigener Recorder schreibt Messwerte in die grosse Postgres.

## Was noch extern ist (Interim) und der Weg zum Spiegel

- Vorhersage/Luftqualitaet: derzeit oeffentliches Open-Meteo (nutzt fuer
  Deutschland die DWD-ICON-Modelle).
- Amtliche Warnungen: derzeit Bright Sky (DWD-Aufbereitung).

Beides ist im Provider gekapselt; ein Wechsel aendert nur eine Basis-URL.

### Open-Meteo-Spiegel starten

Datei: `docker-compose.openmeteo.yml`. Sie startet einen API-Dienst (Port 6154)
und Sync-Dienste, die die DWD-ICON-Modelldaten in ein Volume laden.

```bash
docker compose -f docker-compose.openmeteo.yml up -d
```

Danach den Spiegel in der `.env` aktivieren:

```
OPEN_METEO_BASE=http://localhost:6154/v1
```

Der Provider-Code (`backend/src/wetterwarte/providers/openmeteo.py`) bleibt
unveraendert - nur die Herkunft der Daten wechselt.

Hinweise:
- Host-Entscheidung: in der Entwicklung auf dem Mac (localhost, vom Backend
  erreichbar), im Betrieb auf dem Pi. Datenverzeichnis auf dem Pi auf die externe
  SSD `/mnt/data` legen.
- Speicher/Bandbreite: ein Basis-Setup (DWD-ICON) belegt einige GB; die
  Sync-Dienste laden regelmaessig nach. Mit kleinem `--past-days` bleibt das Volume klein.
- ARM64 (Mac/Pi): liegt kein passendes Image-Manifest vor, das Image lokal bauen:
  `docker buildx build --platform linux/arm64 -t open-meteo:lokal .` (im geklonten
  open-meteo-Repo) und im Compose statt `ghcr.io/open-meteo/open-meteo` verwenden.
- Die genauen Sync-Variablen/Kommandos gegen die installierte Image-Version pruefen
  (`docker run ghcr.io/open-meteo/open-meteo --help`).

### Eigener DWD-Ingester (Warnungen, Radar)

Ziel: Bright Sky als Warnungs-Quelle durch einen eigenen Ingester ersetzen, der
direkt `opendata.dwd.de` bzw. den DWD-GeoServer (`maps.dwd.de`) liest:

- Warnungen: DWD-GeoServer WFS (CAP/NowCastMIX) je Warnzelle/Landkreis, periodisch
  in eine Tabelle `warnungen` schreiben; der Endpunkt liest daraus.
- Radar: RADOLAN-Komposit (opendata.dwd.de) fuer die Radar-Kachel und den
  Regen-Nowcast.
- Beobachtungen: der bestehende Recorder ist bereits ein Ingester fuer
  Stationsmesswerte in die Postgres; er wird um MOSMIX-Vorhersagen erweitert.

Status: Open-Meteo-Spiegel und der DWD-Ingester sind vorbereitet und dokumentiert;
die Umschaltung erfolgt, sobald der Spiegel befuellt bzw. der Ingester aktiv ist.
