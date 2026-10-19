# Wetterwarte - Fahrplan

Stand: Projektsichtung vom 19.10.2026, Fassung 0.46.4. Die frühere Bestandsaufnahme ist weitgehend
abgearbeitet (Radar, Overlays, Layout-Verwaltung, Aufzeichnung, Hilfe, Deep-Links) und hier ersetzt.
Die Telefonansicht steht in [TELEFON.md](TELEFON.md). Pfade relativ zu `backend/src/wetterwarte/`
bzw. `frontend/src/`.

## Sofort: Wahrheit der Daten und Schutz

- **Platzhalterdaten aus dem Produktivpfad** - Kacheln fallen auf erfundene Werte zurück, solange
  nichts geladen ist oder die Quelle ausfällt (`Aktuell`, `Stunden`, `Tage`, `Wind`, `Uv`, `Barometer`,
  `Verlauf`, `Luftqualitaet`, `Nowcast` über `?? platzhalter`). Die Warnkachel zeigt bis zum Laden eine
  erfundene Warnung "Markantes Gewitter, Stufe 3" (`lib/platzhalter.ts:56`). `datenquelle.svelte.ts:47`
  schluckt Fehler, bei totem Backend bleiben Scheindaten dauerhaft stehen. Lösung: Quellen bekommen
  Zustand `laedt/ok/alt/fehlt` und Stand, jede Kachel einen ehrlichen Zustand.
- **Warnungen: Ausfall sieht aus wie "keine Warnungen"** - `routers/weather.py:104` gibt bei Fehler
  eine leere Liste. Sicherheitsrelevant. Lösung: Status je Bereich, Oberfläche zeigt "Warnlage unbekannt".
- **Warnzeiten falsch** - Bright Sky wird ohne `tz` abgefragt und liefert UTC, die Anzeige schneidet
  die Uhrzeit aus dem Text (`providers/warnungen.py:10-22`). Lösung: `tz` = Zeitzone des Orts.
- **gridstack am Telefon kann Desktop-Layouts überschreiben** - unter 768 px schreibt gridstack
  1-Spalten-Werte, nach Hinzufügen oder Entfernen speichert `Brett.svelte` sie per PUT
  (`lib/Brett.svelte:43-64, 123-131`). Im Quelltext nachvollzogen, am Gerät noch nicht. Lösung bis zur
  Telefonansicht: im 1-Spalten-Modus statisch und ohne Speichern.
- **Unsichtbarer Entfernen-Knopf ohne Rückfrage** - Kachelwerkzeuge sind bis `:hover` durchsichtig,
  am Touchgerät aber antippbar (`app.css:945`, `lib/Kachel.svelte:54`).
- **Offene Schreibrouten im Netz** - keine Anmeldung, der Backend-Port 8060 ist im LAN offen
  (`docker-compose.prod.yml:43-45`), `/api/docs` ebenso. Jeder im Netz kann Orte und Layouts löschen,
  den Füll-Bot starten oder die Radar-Aufbewahrung beliebig hoch setzen (Platte). Lösung: Port nur für
  die Kompat-Schicht, Schreibrouten nur über die Oberfläche, Grenzen serverseitig.

## Hoch: Zeitstempel und Datenqualität

- **Zeitstempel durchgehend mit Zeitzone** - Alle Spalten sind `TIMESTAMP` ohne Zone, drei Zeitbasen
  gemischt: Nachtrag in Berliner Ortszeit (`providers/openmeteo.py:82`), Live-Werte per `datetime.now()`
  in Containerzeit, also UTC (`recorder.py:88`), Radar-Archiv mit veraltetem `utcnow`
  (`radar_archiv.py:46,67`). Archivabschnitte sind dadurch 1 bis 2 h versetzt, Mac und Pi rechnen
  verschieden. Der Ausfall der Klimadaten (500 bei `/klima`, `/messjahre`) war ein Folgefehler: eine
  neuere sqlmodel-Fassung lehnt naive Zeitstempel ab. Abgefangen durch Bau nach `uv.lock` (0.46.3),
  die Ursache bleibt. Lösung: `zeit.py` mit `jetzt()` in UTC, Felder `DateTime(timezone=True)`,
  Migration `ALTER ... TYPE timestamptz USING zeit AT TIME ZONE 'UTC'`, Nachtragszeilen aus Berliner
  Zeit umrechnen, Prognosewerte aus dem Nachtrag löschen (`forecast_days=1` liefert auch kommende
  Stunden), Tages- und Monatsgrenzen je Ortszeitzone, API immer ISO 8601 mit Offset. Vorher an einer
  Kopie der Datenbank zählen.
- **Migrationen mit Alembic** - heute `create_all` plus handgeschriebene `ALTER` bei jedem Start
  (`db.py:40-46`). Typwechsel, Indizes und Eindeutigkeit gehen so nicht. Alembic steht schon in den
  Abhängigkeiten.
- **Radar-Rendern blockiert den Server** - Dekodieren und Zeichnen laufen synchron im Event-Loop
  (`routers/radar.py:119-147`), gemessen 270 ms je Bild am Mac, je neuem Vorhersagelauf 24 Bilder. Auf
  dem Pi stehen dann alle Anfragen. Lösung: `asyncio.to_thread` oder eigener Prozess.
- **Fehler protokollieren** - im ganzen Backend kein Logging, breite `except Exception` ohne Spur
  (`cache.py`, `routers/weather.py`, `recorder.py`, `warnpolygone.py`). Grundlage für Status je Bereich.
- **Recorder entkoppeln** - ein einziges `try` für Schreiben, Aggregat und Radar-Schnappschuss
  (`recorder.py:99-144`): scheitert das Aggregat, fehlt auch das Radar. Während der Klima-Ausfälle ist
  vermutlich eine Lücke in der Aufzeichnung entstanden (prüfen). Dazu: Eindeutigkeit auf
  (ort, variable, zeit), ungerundete Werte speichern (heute UI-gerundet über `openmeteo.py:122-138`).

## Mittel

- **Verbundindex und Vollscans** - `messwert` wächst um rund 470 000 Zeilen je Ort und Jahr, hat drei
  Einzelindizes statt (ort, variable, zeit). `/messjahre` aggregiert bei jedem Aufruf den ganzen Ort neu
  (`routers/weather.py:220`), `/aufzeichnung` zählt die ganze Tabelle. `/archiv/verlauf` roh schneidet
  mit `ORDER BY zeit LIMIT 3000` die neuesten Werte ab (`routers/archiv.py:61`).
- **Ort löschen kaskadieren** - Messwerte, Aggregate und Klima bleiben verwaist, ein neuer Ort mit
  gleichem Kürzel erbt sie (`routers/orte.py:68-74`).
- **Daten je Kachel nur, was sie braucht** - jede Kachel abonniert alle fünf Bereiche
  (`lib/ortdaten.svelte.ts:39-45`); die Registry soll `bereiche` je Typ nennen.
- **Abrufe in Effekten mit Abbruch** - Klima, Jahresmesswerte, Archiv und Kopfsuche ohne
  AbortController, Wettläufe bei Orts- oder Jahreswechsel.
- **Beim Zurückkehren alles Veraltete nachladen** - heute nur Warnungen und Blitze
  (`lib/wetter.svelte.ts:99-103`).
- **Blitz-WebSocket neu verbinden** - wird geschlossen, aber nie neu aufgebaut, der Schalter bleibt an
  (`lib/Karte.svelte:709`).
- **MiniKarte** - Radar wird vor `load` angelegt und erscheint erst nach 5 Minuten (`lib/MiniKarte.svelte:241-267`),
  bis zu 20 000 Blitze bei jeder Kartenbewegung.
- **Eine Wahrheit je Sache** - Kachelzuordnung doppelt (`KachelKoerper.svelte` und `registry.ts`),
  Hilfethemen je Typ getrennt (`Kachel.svelte:25-36`), Takt doppelt (`FrischeRing.svelte:7`,
  `datenquelle.svelte.ts:14`), zwei Kartenmodelle (`karteEinst` und `conf` je Kachel). Tote Optionen:
  Feldarten `zahl`/`schalter`, `blitzeLimit`.
- **Gemeinsamer HTTP-Client mit Gesamtfrist** - je Abruf ein neuer Client, `/complete` kann bis
  45 s dauern. Kompat-Schicht ruft Open-Meteo ohne Cache und mit fester Zeitzone Berlin (`routers/kompat.py`).
- **Kachelcache begrenzen** - Anbieter nicht gegen die Liste geprüft, keine Plattengrenze
  (`kachel_cache.py`).

## Gestaltung und Bedienung

- **Schrift zu klein** - Grundschrift 14,5 px, 99 Angaben unter 15 px, Diagramme mit 7 bis 10 px
  (`app.css`, `LinienChart.svelte`, `Klima.svelte`, `Wind.svelte`). Ziel: Skala als Variablen,
  Grundschrift 17 px, klein 15 px, Marken 13 px, Schriftstufen in den Einstellungen.
- **Erklärungen nur per Überfahren** - `lib/tipp.ts` hört nur auf Maus und Fokus, Diagrammblasen
  blitzen am Touchgerät nur auf. Das Telefon bekommt eigene Antipp-Erklärungen (siehe TELEFON.md).
- **PWA-Kopf** - `theme-color` fest weiß auch im dunklen Thema, im Manifest fehlen `id`, `scope`,
  `lang`, keine Sicherheitsbereiche, `100vh` statt `100dvh`. Wird mit der Telefonansicht gelöst.
- **Umlaute in UI-Texten** - "ausser" (`KachelEinstellungen.svelte:130`), "waehlen"
  (`Layouts.svelte:82-83`), "Grosse Karte oeffnen" (`MiniKarte.svelte:304`).
- **Kleinkram** - `svelte-check` meldet einen Fehler (`HilfeLink.svelte`: `children` als Funktion statt
  Snippet), Untertitel "48 Stunden" bei höchstens 18, Nowcast-Text "3 Stunden" bei 90 Minuten Achse,
  Breakpoint 720 neben 768, tote Mockup-CSS in `app.css`, `/health` doppelt abgefragt, LAN-Adressen als
  Rückfall in `vite.config.ts`.

## Erledigt in dieser Runde

- 0.46.3: Backend-Abbild baut exakt nach `uv.lock` (Ursache des Klima-Ausfalls auf dem Pi).
- 0.46.4: Alten Service Worker der Vorgänger-App abgeräumt, Schale und Dateien ohne Prüfsumme nie
  zwischengespeichert, fehlende Dateien liefern 404 statt der Startseite, uv-Abbild fest.
- API-Doku: Ersetzungsfehler "Kölnone" statt "Zeitzone" repariert.
- 0.47.0: Alembic mit Grundstand; alle Zeitspalten mit Zeitzone, alte Werte je Herkunft umgerechnet,
  Vorhersagezeilen aus dem Nachtrag gelöscht, Messwerte eindeutig mit Verbundindex, Monate und
  Archivmittel in Ortszeit, Warnzeiten in Ortszeit. Status je Datenbereich (ok, alt, fehlt), Ausfall
  der Warnquelle nie als leere Liste, Logging statt verschluckter Fehler, Aufzeichnung ungerundet und
  je Schritt abgesichert, Radar-Rendern außerhalb des Event-Loops, Radar-Archiv höchstens zwei Wochen,
  Kompat-Schicht über den gemeinsamen Zwischenspeicher, Antworten komprimiert, Telefon-Endpunkt.
- 0.47.1: Keine Platzhalterdaten mehr in Desktop-Kacheln (Kachelhülle zeigt Laden, Ausfall, Alter),
  Katalog einzige Wahrheit für Komponente, Daten und Hilfethema, schmale Fenster überschreiben keine
  Desktop-Layouts mehr, Kachel-IDs ohne `crypto.randomUUID`, Nowcast-Achse richtig, gemeinsamer Kern.
- Telefonansicht und Telefon-Editor nach [TELEFON.md](TELEFON.md); Kachelzwischenspeicher prüft
  Anbieter und Kachelnummern; Umlaute in drei UI-Texten; `HilfeLink` als Snippet getypt.
- 0.49.0: Aktive Warnungen nach [WARNUNGEN.md](WARNUNGEN.md): Lage je Ort aus Radar-Nowcast, Modell,
  amtlichen Warnungen und Blitzen; Mitteilungen aufs Telefon mit Buchführung je Gerät, Nachtruhe und
  Entwarnung; Tonansagen mit der Zeit-Stimme; sichere Adresse über Caddy. Radarwerte jetzt in mm/h
  (RADOLAN liefert Höhe je 5 Minuten, Karte und Legende zeigten zwölffach zu wenig). Desktop-Kachel
  Regen-Nowcast aus derselben Quelle wie Telefon und Meldungen (Radar vor Modell). Ohne WebGL zeigen die
  Karten einen Hinweis, statt die Desktop-Ansicht mitzureißen. Einheiten in Telefonkacheln ausgeschrieben.
  README-Bild aus der echten App mit Demo-Orten (`tools/readme-bild.mjs`, `mockups/praesentation.html`).
- 0.49.1: Eigenes App-Symbol (`frontend/public/symbol.svg`, kräftiger Himmel statt blasser Wolke auf Grau);
  alle Symbole für Startbildschirm und Manifest deckend und randlos (iOS 18 nimmt die Manifest-Symbole und zeigt
  durchsichtige nicht), erzeugt mit `tools/symbole.py` nach der Vorlage des Appkerns.
- 0.49.2: Seiten melden nur PNG-Symbole (wie die Kiste). Mit favicon.ico `sizes="any"` und SVG-Symbol zeigte das
  iPhone beim Hinzufügen zum Home-Bildschirm nur den Anfangsbuchstaben (auch die Transkription). Caddy ohne
  HTTP/3, das er auf dem falschen Port ankündigte.

## Reihenfolge (offen)

1. Schreibrouten absichern und Backend-Port nur für die Kompat-Schicht öffnen; unsichtbarer
   Entfernen-Knopf der Desktop-Kacheln am Touchgerät.
2. Mittel-Punkte: Verbundindex ist da, Vollscans in `/aufzeichnung` und `/archiv/variablen` bleiben;
   Ort löschen kaskadieren; Abrufe in Effekten mit Abbruch; Blitz-WebSocket neu verbinden; MiniKarte.
3. Gestaltung am Desktop: Schriftskala 17/15/13 wie am Telefon, Erklärungen ohne Überfahren.
