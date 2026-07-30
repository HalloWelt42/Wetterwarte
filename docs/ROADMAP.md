# Wetterwarte - Fahrplan (Bestandsaufnahme)

Priorisierte Bestandsaufnahme: tote Mockup-UI, Redundanzen, Architektur, fehlende Bereiche. Aufwand S/M/L.

## Sofort aufraeumen (Redundanzen + toter Code)

- **Tote Kopf-Ortssuche entfernen oder anbinden** (hoch, S) - Das grosse Suchfeld im Kopf hat kein Binding und dupliziert die einzig funktionierende Ortssuche im Overlay; entweder an `ui.ortssuche=true` binden oder ersatzlos raus. Dateien: `frontend/src/lib/Kopf.svelte`, `frontend/src/lib/Ortssuche.svelte`, `frontend/src/lib/Nav.svelte`, `frontend/src/app.css` (182-197).
- **Totes 12-Spalten-Grid entsorgen** (mittel, M) - `.brett`/`.w2-.w12`/`.h1-.h5` werden an kein Element mehr vergeben, da gridstack die Groessen ueber `gs-w/gs-h` steuert. Dateien: `frontend/src/app.css` (620-644, 2012-2017), `frontend/src/lib/Brett.svelte` (170).
- **Mockup-Restklassen aus app.css raeumen** (mittel, M) - Rund 40 nirgends referenzierte Selektoren (`.handy*`, `.mock-leiste`, `.galerie*`, `.nutzer-chip`, `.tchart` u.a.) als toter Ballast aus der Mockup-Aera. Dateien: `frontend/src/app.css` (138-150, 243-266, 405-420, 927, 1075-1088, 1771-1955, 2021-2068).
- **Archiv-Chart-Geometrie eindampfen** (mittel, S) - Das `chart`-Derived berechnet SVG-Pfade `linie`/`flaeche`/`x()`/`y()`, die im Template nie ausgegeben werden (rendert `LinienChart`); nur `lo/hi/mittel` bleiben noetig. Dateien: `frontend/src/lib/Archiv.svelte` (42-56), `frontend/src/lib/LinienChart.svelte`.
- **Ungenutzten `orte`-Export streichen** (niedrig, S) - `platzhalter.ts` exportiert fuenf Demo-Orte, die niemand importiert. Dateien: `frontend/src/lib/platzhalter.ts` (6-12).
- **Orts-Query zentralisieren** (niedrig, S) - Router `liste()` dupliziert exakt `ortsdienst.alle()`, statt es aufzurufen; Sortierlogik gehoert an eine Stelle. Dateien: `backend/src/wetterwarte/routers/orte.py` (47-49), `backend/src/wetterwarte/ortsdienst.py` (13-16).
- **Docstring-Widerspruch beim Orte-Seed aufloesen** (niedrig, S) - Modul-Docstring behauptet "keine verdrahteten Orte", doch fuenf Orte werden beim Erststart geseedet; Docstring praezisieren oder Seed entfernen. Dateien: `backend/src/wetterwarte/routers/orte.py` (3-5), `backend/src/wetterwarte/orte.py`, `backend/src/wetterwarte/db.py`.
- **Envelope/Meta-Modelle klaeren** (niedrig, S) - `schemas/envelope.py` definiert getypte Modelle, die kein Router nutzt (alle bauen den Umschlag per `wrap()`); als `response_model` einsetzen oder loeschen. Dateien: `backend/src/wetterwarte/schemas/envelope.py`, `backend/src/wetterwarte/routers/weather.py`.
- **Magischen `koeln`-Default ersetzen** (niedrig, S) - Koeln steht als fester Default in Archiv-Router, `wetter.svelte.ts` und `App.svelte`; aus dem Start-Ort ableiten (`startOrt()` existiert). Dateien: `backend/src/wetterwarte/routers/archiv.py`, `frontend/src/lib/wetter.svelte.ts`, `frontend/src/App.svelte`.

## Tote Mockup-UI real umsetzen (nach Bereich)

- **Layout-Verwaltung an die API haengen** (hoch, L) - `Layouts.svelte` zeigt ein hartkodiertes Array und die Knoepfe Umbenennen/Duplizieren/Loeschen/Neu haben keine Handler, obwohl POST/PUT/DELETE im Backend fertig sind. Dateien: `frontend/src/lib/Layouts.svelte`, `backend/src/wetterwarte/routers/layouts.py`, `frontend/src/lib/layout.svelte.ts`.
- **Aufzeichnungs-Manager funktional machen** (hoch, L) - Vier fest eingetragene Stationen, nur lokaler State, keine Persistenz und kein Recording-Router; die Auswahl muss ans Backend, das `recorder.schleife()` bereits laeuft. Dateien: `frontend/src/lib/Aufzeichnung.svelte`, `backend/src/wetterwarte/main.py`, `backend/src/wetterwarte/recorder.py`.
- **Fehlende Kacheltypen umsetzen** (hoch, L) - Rund 13 der 27 im Katalog gezeichneten Typen fehlen in Registry und Renderer (Mini-Kachel, Orte-Vergleich, Wetterbericht/LLM, Komfort, Niederschlag/Schnee, Sicht/Nebel, Rekorde, Heatmap, Schwellenwert-Alarm, Datenquellen/Status u.a.). Dateien: `frontend/src/lib/kacheln/registry.ts`, `frontend/src/lib/kacheln/KachelKoerper.svelte`, `mockups/katalog.html`. (Sinnvoll erst nach der Modularisierung, siehe Architektur.)
- **Mini-i-Hilfeknoepfe an den Kacheln nachruesten** (hoch, S) - Der Kachelkopf hat nur Einstellungen und Entfernen; die in `Hilfe.svelte` beworbenen i-Symbole mit Tiefenlink fehlen komplett. Dateien: `frontend/src/lib/Kachel.svelte`, `frontend/src/lib/Hilfe.svelte`.
- **Pro-Kachel-Einstellungen vervollstaendigen** (mittel, M) - Es fehlen vor allem der Ort-pro-Kachel-Selektor sowie Intervall, Groesse und Icon-Stil; alle Kacheln haengen am globalen aktiven Ort. Dateien: `frontend/src/lib/KachelEinstellungen.svelte`, `frontend/src/lib/kacheln/registry.ts`, `mockups/kachel-einstellungen.html`.
- **Archiv-Panels Klima-Abweichung und Jahres-Heatmap bauen** (mittel, M) - Zwei der drei Mockup-Panels fehlen; Backend liefert nur `/archiv/verlauf`, keine Rekord-/Anomalie-/Heatmap-Endpunkte. Dateien: `frontend/src/lib/Archiv.svelte`, `backend/src/wetterwarte/routers/archiv.py`, `mockups/archiv.html`.
- **Tote Suchfelder verdrahten oder entfernen** (mittel, M) - Kacheltyp-Suche im Katalog und Stationssuche in der Aufzeichnung tun nichts (Kopf-Suche siehe oben); filterbar machen oder streichen. Dateien: `frontend/src/lib/Katalog.svelte`, `frontend/src/lib/Aufzeichnung.svelte`.

## Grosse Bereiche (Karten/Radar, Gestaltung/Hilfe)

### Karten und Radar

- **Dashboard-Karten-Kachel auf echtes MapLibre umstellen** (hoch, M) - Der `karte`-Zweig rendert hartkodierte `.radar-blob`-Divs und ein gemaltes Standbild statt einer Karte; muss denselben Renderer wie die Vollansicht nutzen. Dateien: `frontend/src/lib/kacheln/KachelKoerper.svelte` (167-179), `frontend/src/app.css` (915-957), `frontend/src/lib/Karte.svelte`.
- **RADOLAN-Radar als Provider/Endpoint/Layer bauen** (hoch, L) - Es gibt keinerlei Radar-Implementierung; die Attributionen "DWD RADOLAN" sind aktuell unwahr. Dateien: `backend/src/wetterwarte/providers/`, `backend/src/wetterwarte/routers/weather.py`, `frontend/src/lib/Karte.svelte`.
- **Overlay-Schalter an die Map anbinden** (hoch, L) - Radar/Nowcast/Wind/Temperatur/Warnungen/Blitze toggeln nur ein Boolean, das niemand liest; `map.addLayer/removeLayer` per `$effect` fehlt. Dateien: `frontend/src/lib/Karte.svelte` (7-14, 63-74).
- **Radar-Zeitleiste zum Frame-Loop machen** (hoch, L) - Play-Knopf ohne Handler, Scrubber fest bei `left:66%`, keine Zeitschritte; taeuscht eine Animation nur vor. Dateien: `frontend/src/lib/Karte.svelte` (77-92). (Haengt am RADOLAN-Backend.)
- **Warn-Polygone durchreichen und zeichnen** (mittel, M) - Provider verwirft die Geometrie und liefert nur Stufe/Titel/Zeit; ohne Polygon kein Warn-Layer. Dateien: `backend/src/wetterwarte/providers/warnungen.py`, `frontend/src/lib/Karte.svelte`.
- **Blitz-Marker ermoeglichen** (mittel, S) - Rohdaten enthalten lat/lon, doch der Provider reduziert jeden Strike auf Zeit/Distanz-Text; Koordinaten durchreichen. Dateien: `backend/src/wetterwarte/providers/blitze.py`, `frontend/src/lib/Karte.svelte`.
- **Karte an aktiven Ort koppeln plus Geolocate/Popup** (mittel, S) - Center steht fest auf `[12.14, 51.05]` (liegt bei Leipzig, nicht Koeln), Ortswechsel bewegen nichts, "Mein Standort" und Klick-Popup fehlen. Dateien: `frontend/src/lib/Karte.svelte` (41), `frontend/src/lib/orte.svelte.ts`.
- **Basiskarten-Umschalter Dunkel/Satellit anbinden** (mittel, M) - Die Buttons setzen nur State, es gibt nur die eine Colorful-Rasterquelle, `setStyle` fehlt. Dateien: `frontend/src/lib/Karte.svelte` (6, 58-62).
- **Welt-Tile-Proxy und Zoom-Grenze nutzen** (niedrig, M) - Ausserhalb DE bleibt die Karte grau; der lightningmap-Weltproxy ist ungenutzt, Zoom nicht auf 0-14 begrenzt. Dateien: `frontend/src/lib/Karte.svelte` (29-44).
- **Wind-Partikel- und Temperatur-Flaechen-Overlay** (niedrig, L) - Neuentwicklung inkl. ICON-Gitterdatenquelle. Dateien: `frontend/src/lib/Karte.svelte` (19-20).

### Gestaltung und Hilfe

- **Kachel-Zustaende Laden/Skelett/Leer/Fehler mit Retry** (hoch, L) - Die CSS-Klassen `.sk`/`@keyframes schimmer`/`.kw-fehler` existieren, werden aber in keiner Komponente verwendet; Fehler werden still verschluckt. Dateien: `frontend/src/lib/wetter.svelte.ts` (46-65), `frontend/src/lib/kacheln/KachelKoerper.svelte`, `frontend/src/app.css` (1736-1768). (Deckt sich mit dem Architektur-Punkt zu Platzhaltern.)
- **Handy-Navigation herstellen** (hoch, L) - Ab 720px werden Nav und Layout-Tabs ausgeblendet, ohne Ersatz; der im Mockup vorgesehene Hamburger/Drawer fehlt, sodass auf dem Handy nur das Dashboard erreichbar ist. Dateien: `frontend/src/lib/Kopf.svelte`, `frontend/src/app.css` (1993-2019), `mockups/handy.html`.
- **Hilfe durchsuchbar und verschiebbar machen** (hoch, M) - Das Suchfeld hat kein Binding/keinen Filter, und trotz `cursor:move` fehlt jede Drag-Logik; beide Kernattribute der Vorgabe fehlen. Dateien: `frontend/src/lib/Hilfe.svelte`, `frontend/src/app.css` (1826-1833).
- **Umlaut-Verstoesse in UI-Texten fixen** (hoch, S) - "Suche laeuft ...", "Archiv wird noch befuellt ...", "Hoechster Tageswert" verletzen die Umlaut-Regel. Dateien: `frontend/src/lib/Ortssuche.svelte` (60), `frontend/src/lib/Archiv.svelte` (99, 113).
- **Ist-Zustand persistieren** (mittel, M) - Theme, Atmosphaere und aktives Layout leben nur im RAM; kein localStorage, keine Beachtung der System-Praeferenz beim ersten Laden. Dateien: `frontend/src/lib/thema.svelte.ts`, `frontend/src/lib/stil.svelte.ts`, `frontend/src/lib/layout.svelte.ts`.
- **Katalog um Drag und Vorschau erweitern** (mittel, L) - Nur Klick-Hinzufuegen, generischer Untertitel "Kachel hinzufuegen", kein Drag und keine Kurzbeschreibung. Dateien: `frontend/src/lib/Katalog.svelte`.
- **Atmosphaere an Tageszeit koppeln** (niedrig, M) - `.atmo.sonnenuntergang` ist toter Verlauf, weil `stimmungFuer()` ihn nie erzeugt und nur das Wetter-Icon statt des Sonnenstands auswertet. Dateien: `frontend/src/App.svelte` (28-35), `frontend/src/app.css` (1866-1886).
- **Tastatur/ESC und Fokus-Management ergaenzen** (niedrig, M) - Kein Modal schliesst per Escape, kein Fokus-Trap, keine Fokus-Rueckgabe. Dateien: `frontend/src/lib/KachelEinstellungen.svelte`, `frontend/src/lib/Katalog.svelte`, `frontend/src/lib/Hilfe.svelte`.
- **Tooltips vereinheitlichen** (niedrig, S) - Native `title`-Attribute (Kachel, Kopf, Nav, Layouts) auf das vorhandene `use:tipp`-System umstellen. Dateien: `frontend/src/lib/Kachel.svelte`, `frontend/src/lib/Kopf.svelte`, `frontend/src/lib/tipp.ts`.

## Architektur und Tests (sauber, modular, testbar halten)

- **KachelKoerper in pro-Typ-Komponenten zerlegen** (hoch, L) - 15 Typen in einer `{#if}`-Kette mit gemeinsamer Rechenlogik; ein Feld `komponente` in `KachelDef` plus `<svelte:component>` macht die geplanten 28 Typen skalierbar und ist Voraussetzung fuer den Katalog-Ausbau. Dateien: `frontend/src/lib/kacheln/KachelKoerper.svelte`, `frontend/src/lib/kacheln/registry.ts`, `frontend/src/lib/Kachel.svelte`.
- **Platzhalter aus dem Produktivpfad ziehen** (hoch, M) - `wetter.aktuell ?? aktuell` zeigt bei Backend-Ausfall erfundene Koeln-Daten als echt; `wetter.geladen` plus Ladestatus-Enum sollen echte Leer/Fehler-Zustaende rendern, Fixtures nur im Vorschau-Pfad. Dateien: `frontend/src/lib/kacheln/KachelKoerper.svelte`, `frontend/src/lib/platzhalter.ts`, `frontend/src/lib/wetter.svelte.ts`. (Gemeinsam mit dem Zustands-Punkt oben umsetzen.)
- **Testfundament schaffen** (hoch, M) - Kein einziger Test; pytest+respx fuer die Provider-Normalisierung, vitest+@testing-library/svelte fuer Chart-Geometrie/Mondphase/Sonnenbogen. Dateien: `backend/pyproject.toml`, `frontend/package.json`, `backend/src/wetterwarte/providers/openmeteo.py`, `providers/pollen_dwd.py`.
- **Fachwerte auf eine Quelle der Wahrheit** (mittel, M) - Pollenarten/Schadstoffe/Schwellen und die AQI-Bewertung liegen doppelt in Backend und Frontend und divergieren bereits (`<=40 gut` vs. `<=60 warn`); Labels/Schwellen backend-autoritativ liefern. Dateien: `frontend/src/lib/kacheln/registry.ts`, `backend/src/wetterwarte/providers/pollen_dwd.py`, `providers/luftqualitaet.py`, `frontend/src/lib/kacheln/KachelKoerper.svelte`.
- **Brett.svelte entflechten** (mittel, M) - Grid-Lifecycle, Persistenz, Store-Bruecken und Migration in einer Datei; `addWidget/removeWidget` statt `destroy`+`init` bei jeder Mutation, gridstack in eine eigene Komponente kapseln. Dateien: `frontend/src/lib/Brett.svelte`, `frontend/src/lib/kachelAktion.svelte.ts`, `frontend/src/lib/kachelConf.svelte.ts`.
- **Verschluckte Exceptions protokollieren** (mittel, M) - Breite `except Exception: return None` ohne Logging machen dauerhafte Provider-Ausfaelle unsichtbar; je Provider `logging.warning` plus letzter Erfolg/Fehler als Basis fuer die geplante Status-Kachel. Dateien: `backend/src/wetterwarte/routers/weather.py`, `recorder.py`, `cache.py`.
- **Wiederholte Inline-Styles in Komponenten fassen** (niedrig, S) - Vier identische Kennzahl-Karten und lange Panel-Styles gehoeren in eine `Kennzahl.svelte` bzw. CSS-Klassen. Dateien: `frontend/src/lib/Archiv.svelte`, `frontend/src/lib/Karte.svelte`.

## Empfohlene Reihenfolge

1. **Sofort-Aufraeumen komplett** - tote Kopf-Suche, Grid-Reste, app.css-Ballast, Archiv-Geometrie und die kleinen Backend-Dubletten; billige Punkte, die die Codebasis vor dem Umbau entschlacken.
2. **Umlaut-Fixes** - drei Strings, hoechste Regel-Prioritaet, in Minuten erledigt.
3. **Modularisierung KachelKoerper plus echte Kachel-Zustaende** - pro-Typ-Komponenten und Laden/Leer/Fehler/Retry statt stiller Platzhalter; Fundament fuer alles Weitere, macht die Logik zugleich testbar.
4. **Testfundament einziehen** - direkt nach der Modularisierung, solange die Helfer frisch extrahiert sind.
5. **Fehlende Kacheltypen und Pro-Kachel-Ort/Intervall** - auf der neuen Registry-Struktur den Katalog fuellen.
6. **Layout-Verwaltung und Aufzeichnungs-Manager an die API** - die beiden groessten Attrappen mit teils schon vorhandenem Backend.
7. **Karten-Block** - erst echte Dashboard-Karte und Ortskopplung, dann RADOLAN-Backend, darauf Overlays/Zeitleiste/Marker/Polygone.
8. **Gestaltungs- und Hilfe-Politur** - Handy-Navigation, durchsuchbare/verschiebbare Hilfe, Mini-i-Knoepfe, Persistenz und a11y zum Abschluss.
