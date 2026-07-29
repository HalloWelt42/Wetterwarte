# Wetterwarte

Eine eigenstaendige, weitgehend unabhaengige Wetter-App fuer den Browser (Desktop und Handy).
Kern ist eine komplett kachelbasierte Oberflaeche: Kacheltypen werden per Drag-and-Drop frei
angeordnet und in der Groesse gezogen. Ausser den reinen Wetterdaten laeuft alles lokal; eine
grosse PostgreSQL zeichnet ausgewaehlte Stationen und Orte langfristig auf.

## Aufbau

```
backend/     FastAPI (SQLModel, asyncpg, Alembic) - API und Datenschicht
frontend/    Svelte 5 + Vite + TypeScript - kachelbasiertes Dashboard
mockups/     Durchklickbares HTML/CSS-Mockup (verbindliche Design-Vorlage)
tools/       setup-env.sh (projekt-eindeutige Ports und Namen via cksum)
docker-compose.yml   Postgres und Redis (nur als Container)
wetter       Einstiegspunkt fuer Einrichtung und Betrieb
```

## Entwicklung

Voraussetzungen: Docker, Node.js, uv (Python).

```bash
./wetter setup     # erzeugt .env mit eindeutigen Ports und Passwoertern
./wetter up        # startet Postgres und Redis als Container
```

Danach die Entwicklungsserver auf dem Host starten:

```bash
cd backend  && uv run uvicorn wetterwarte.main:app --reload --port <BACKEND_PORT>
cd frontend && npm install && npm run dev
```

Die Ports stehen in der erzeugten `.env` (Standardbereich ab 6150). Das Frontend spricht das
Backend same-origin ueber den Vite-Proxy an (kein CORS noetig).

## Design-Vorlage ansehen

Das durchklickbare Mockup ist der verbindliche Design-Leitfaden. Die App uebernimmt dessen Optik
1:1. Ansehen:

```bash
./wetter mockup
```

Galerie: `http://localhost:6159/mockups/index.html`

## Datenquellen

Wetterdaten kommen von den offiziellen, freien Quellen (Deutscher Wetterdienst fuer Deutschland,
Open-Meteo weltweit) und werden lokal aufbereitet und gecacht. Kartenmaterial stammt aus
OpenStreetMap und wird lokal gehostet. Schrift (Barlow) und Icons werden lokal gebuendelt, ohne
externe Netzwerkabrufe.
