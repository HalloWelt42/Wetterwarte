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
