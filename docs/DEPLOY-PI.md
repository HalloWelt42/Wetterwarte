# Deployment auf dem Server (Raspberry Pi)

Die Wetterwarte laeuft als eigenstaendige App: ein `docker-compose.prod.yml`
steuert alles (Frontend hinter nginx, Backend, PostgreSQL, Redis). Nur das
Frontend ist nach aussen offen; die Daten liegen auf der externen SSD unter
`DATA_DIR`. Es gibt keine Kopplung an frueher genutzte Dienste.

Server, Ordner und Namen im Zertifikat stehen nicht im Repo: `./wetter deploy`, `./wetter zertifikat` und
`./wetter rauchtest` holen sie mit `handbuch ziel wetterwarte` aus der privaten Wahrheit des Hauses; `PI_HOST`,
`PI_PFAD`, `ZERT_NAMEN` und `WETTERWARTE_ADRESSE` aus der Umgebung gehen vor. Adressen im Heimnetz stehen in
`.env.prod` auf dem Server. Im Folgenden ist `pi@<server>` der Zugang und `<ordner>` der Ordner dort.

## Bausteine

- `backend/Dockerfile` - Backend-Image (FastAPI + uvicorn).
- `frontend/Dockerfile` + `frontend/nginx.conf.template` - gebaute SPA hinter nginx,
  leitet `/api` ans Backend und `/karte` an den lokalen Kartendienst (Adressen aus `.env.prod`).
- `docker-compose.prod.yml` - steuert alle vier Container, `restart: unless-stopped`.
- `.env.prod` - Passwort, Ports, Datenverzeichnis und Adressen im Heimnetz (aus `.env.prod.example`, nie ins Repo).
- `deploy/wetterwarte.service` - systemd-Unit fuer den Autostart beim Booten.
- `tools/sicherung.sh` - Sicherung der Datenbank (`./wetter sicherung`, siehe Abschnitt Sicherung).

## Erstinstallation

```bash
# 1. Quellcode auf den Pi bringen (vom Entwicklungsrechner)
rsync -az --delete \
  --exclude node_modules --exclude .venv --exclude .git \
  --exclude dist --exclude data --exclude '.env*' \
  ./ pi@<server>:<ordner>/

# 2. Auf dem Pi: Umgebung anlegen und Datenverzeichnis vorbereiten
ssh pi@<server>
cd <ordner>
cp .env.prod.example .env.prod   # Passwort setzen, Ports, DATA_DIR und Adressen eintragen
mkdir -p "$DATA_DIR/postgres" "$DATA_DIR/redis"   # DATA_DIR wie in .env.prod

# 3. Bauen und starten (ein Befehl steuert alles)
./wetter prod-up

# 4. Autostart einrichten
sudo cp deploy/wetterwarte.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wetterwarte
```

Die App ist dann unter `http://<server>:<WEB_PORT>` erreichbar.

## Sichere Adresse (HTTPS) für Mitteilungen

Mitteilungen aufs Telefon (Web Push) und der Service Worker brauchen HTTPS. Vor dem Frontend steht dafür
ein Caddy (`vorne` in `docker-compose.prod.yml`, `deploy/Caddyfile`) auf `HTTPS_PORT` (8062) mit dem
Blattzertifikat der Hausstelle, wie bei Kiste, Kellerwolke und Transkription. Die Adresse auf 8061 bleibt.

```bash
./wetter zertifikat   # vom Mac: mit mkcert ausstellen und nach <ordner>/zertifikate legen
./wetter deploy       # danach startet auch der Dienst vorne
```

`./wetter deploy` lässt den Ordner `zertifikate` beim Abgleich stehen. Das Telefon muss der Hausstelle
vertrauen (einmalig eingerichtet). Dann `https://<server>:8062/telefon` öffnen, Teilen, Zum
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
./wetter sicherung      # Datenbank sichern, wenn fällig (siehe Sicherung)
```

## Aktualisieren

Vom Mac `./wetter deploy`: gleicht den Quellcode ab, sichert auf dem Pi die Datenbank (wenn fällig) und baut neu.
Von Hand: neuen Stand per `rsync` (Schritt 1) übertragen, dann auf dem Pi
`./wetter sicherung vor-ausrollen && ./wetter prod-restart`.

## Sicherung

Gesichert wird ein Auszug der Postgres (`pg_dump`, mit `gzip -n` gepackt) nach `DATA_DIR/sicherungen`, je Stand eine
Datei `wetterwarte-JJJJMMTT-hhmmss.sql.gz` (Zeitpunkt, zu dem der Auszug begann; ebenso ihre Änderungszeit). Darin
stehen Profile und Ansichten, Orte, Einstellungen, Geräte samt Schlüssel für Web Push und das Langzeit-Archiv der
Messwerte. Nicht gesichert wird, was von selbst neu entsteht: Redis (Zwischenspeicher mit Ablaufzeit), der
Kachel-Cache und der Inhalt der Tabellen `radararchivframe` (Radarbilder, rollend höchstens zwei Wochen) und
`klimanormale` (holt das Backend bei Bedarf neu); ihr Aufbau ist im Auszug.

Regel (Vorgaben in `tools/sicherung.sh`, in `.env.prod` oder der Umgebung überschreibbar):

- `./wetter sicherung` sichert, wenn die jüngste Sicherung `SICHERUNG_ABSTAND_TAGE` alt ist (Vorgabe 7).
- `./wetter deploy` ruft vor dem Neustart `./wetter sicherung vor-ausrollen`: gesichert wird nur, wenn die jüngste
  älter ist als `SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN` (Vorgabe 24). Scheitert die Sicherung, bricht das Ausrollen ab
  und der laufende Stand bleibt.
- Nie ohne Änderung: gleicht der neue Auszug inhaltlich der jüngsten Sicherung, wird er verworfen.
- Höchstens `SICHERUNG_BEHALTEN` Stände (Vorgabe 3), bei jedem Lauf durchgesetzt. Angefasst werden nur Dateien nach
  dem Muster oben; Teildateien während des Laufs beginnen mit einem Punkt, Begleitdateien gibt es nicht.

Alter wird in ganzen Tagen bzw. Stunden gemessen (gerundet). Ob fällig, entscheidet der Lauf selbst, ein zu früher
Aufruf tut nichts. Regelmäßig ruft ihn cron auf dem Pi, einmal je Woche (`crontab -e` als Nutzer `pi`):

```
15 4 * * 0 <ordner>/wetter sicherung 2>&1 | logger -t wetterwarte-sicherung
```

Ausgaben der Läufe: `journalctl -t wetterwarte-sicherung`.

Zurückspielen (auf dem Pi im `<ordner>`, Datei aus `DATA_DIR/sicherungen`):

```bash
P="docker compose -f docker-compose.prod.yml --env-file .env.prod"
$P stop backend
$P exec -T postgres sh -c 'dropdb -U "$POSTGRES_USER" "$POSTGRES_DB" && createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
gzip -dc <datei> | $P exec -T postgres sh -c 'psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
./wetter prod-up
```
