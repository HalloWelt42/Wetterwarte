# Deployment auf dem Server (Raspberry Pi)

Die Wetterwarte laeuft als eigenstaendige App: ein `docker-compose.prod.yml`
steuert alles (Frontend hinter nginx, Backend, PostgreSQL, Redis). Nur das
Frontend ist nach aussen offen; die Daten liegen auf der externen SSD unter
`/mnt/data`. Es gibt keine Kopplung an frueher genutzte Dienste.

## Bausteine

- `backend/Dockerfile` - Backend-Image (FastAPI + uvicorn).
- `frontend/Dockerfile` + `frontend/nginx.conf` - gebaute SPA hinter nginx,
  leitet `/api` ans Backend und `/karte` an den lokalen Kartendienst.
- `docker-compose.prod.yml` - steuert alle vier Container, `restart: unless-stopped`.
- `.env.prod` - Passwort, Port und Datenverzeichnis (aus `.env.prod.example`, nie ins Repo).
- `deploy/wetterwarte.service` - systemd-Unit fuer den Autostart beim Booten.

## Erstinstallation

```bash
# 1. Quellcode auf den Pi bringen (vom Entwicklungsrechner)
rsync -az --delete \
  --exclude node_modules --exclude .venv --exclude .git \
  --exclude dist --exclude data --exclude '.env*' \
  ./ pi@192.168.178.49:/home/pi/wetterwarte/

# 2. Auf dem Pi: Umgebung anlegen und Datenverzeichnis vorbereiten
ssh pi@192.168.178.49
cd /home/pi/wetterwarte
cp .env.prod.example .env.prod   # Passwort setzen, WEB_PORT/DATA_DIR pruefen
mkdir -p /mnt/data/wetterwarte/postgres /mnt/data/wetterwarte/redis

# 3. Bauen und starten (ein Befehl steuert alles)
./wetter prod-up

# 4. Autostart einrichten
sudo cp deploy/wetterwarte.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wetterwarte
```

Die App ist dann unter `http://192.168.178.49:<WEB_PORT>` erreichbar.

## Sichere Adresse (HTTPS) für Mitteilungen

Mitteilungen aufs Telefon (Web Push) und der Service Worker brauchen HTTPS. Vor dem Frontend steht dafür
ein Caddy (`vorne` in `docker-compose.prod.yml`, `deploy/Caddyfile`) auf `HTTPS_PORT` (8062) mit dem
Blattzertifikat der Hausstelle, wie bei Kiste, Kellerwolke und Transkription. Die Adresse auf 8061 bleibt.

```bash
./wetter zertifikat   # vom Mac: mit mkcert ausstellen und nach /home/pi/wetterwarte/zertifikate legen
./wetter deploy       # danach startet auch der Dienst vorne
```

`./wetter deploy` lässt den Ordner `zertifikate` beim Abgleich stehen. Das Telefon muss der Hausstelle
vertrauen (einmalig eingerichtet). Dann `https://192.168.178.49:8062/telefon` öffnen, Teilen, Zum
Home-Bildschirm, aus dem neuen Symbol starten und unter Mehr, Warnungen aufs Telefon einschalten.

## Rauchtest vor und nach dem Ausrollen

`./wetter rauchtest [adresse]` öffnet jede Ansicht (Desktop und Telefon) in einem kopflosen Chrome und meldet jede
Ausnahme, jeden Konsolenfehler und jede Anfrage mit Status ab 400. Vor dem Ausrollen gegen einen Probelauf des
Produktionsaufbaus (nur dort laufen nginx und Caddy wie im Betrieb; der Entwicklungsserver verdeckt Fehler der
Auslieferung), danach gegen den Pi. Ausgang 1 bei jedem Befund.

## Steuerung

```bash
./wetter prod-up        # bauen + starten
./wetter prod-down      # stoppen
./wetter prod-restart   # neu bauen + starten (nach einem Update)
./wetter prod-status    # Container-Status
./wetter prod-logs      # Logs folgen
```

## Aktualisieren

Neuen Stand per `rsync` (Schritt 1) uebertragen, dann `./wetter prod-restart`.

## Sicherung

Das Datenverzeichnis `/mnt/data/wetterwarte` enthaelt Postgres und Redis.
Fuer ein Backup die App kurz stoppen und den Ordner sichern, oder `pg_dump`
gegen den Postgres-Container laufen lassen.
