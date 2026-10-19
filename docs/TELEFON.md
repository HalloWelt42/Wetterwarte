# Telefonansicht (Entwurf)

Stand: Entwurf zur Freigabe, Fassung 0.46.4. Entwurfsseiten unter `mockups/telefon/`.

## Ziel

Eine eigenständige Ansicht für das Telefon (iPhone als PWA vom Startbildschirm, ebenso andere
Telefone). Keine verkleinerte Desktop-Seite und keine Umbruchpunkte im Desktop-Raster. Geteilt werden
nur Daten, Endpunkte und Rechenkerne. Bedienung, Gestaltung und Kacheln sind eigene.

Am Telefon wird **angezeigt**, nicht eingerichtet. Das Telefon-Layout gehört zum Profil und wird am
Desktop bearbeitet.

## Grundsätze

- Schwarzer Grund, Kacheln als dunkle Flächen ohne Rahmenlinien.
- Nachtbetrieb ausschließlich rot und gedämpft: kein Weiß, kein Blau, keine bunten Zustandsfarben.
  Zustände über Helligkeit und Form. Wettersymbole als einfarbige Masken.
- Grundschrift 17 px, kleine Texte 15 px, Kachelköpfe 13 px. Drei Schriftstufen (Normal, Groß,
  Sehr groß), je Gerät gespeichert. Alle Größen kommen aus einer Skala von Variablen (`--s13` bis
  `--s26`), auch in Diagrammen.
- Berührflächen ab 44 Punkten, nichts hängt am Überfahren.
- `display: standalone`, `viewport-fit=cover`, Sicherheitsbereiche über `env(safe-area-inset-*)`,
  `100dvh`.
- Nie erfundene Werte: Was nicht geladen ist, zeigt einen ehrlichen Zustand (Laden, alt, fehlt).
- Die Seite rollt nie seitlich.

## Bedienkonzept

| Bereich | Inhalt |
|---|---|
| Kopf (steht) | Ort mit Pfeil (Tippen öffnet die Orte), Stand mit Frischepunkt, Punkte für die Orte. Seitlich wischen über dem Kopf wechselt den Ort. |
| Warnband | Erscheint über dem Raster, sobald für den Ort eine Warnung gilt und im Layout keine Warnkachel steht. Fällt die Warnquelle aus, steht dort "Warnlage unbekannt" statt nichts. |
| Raster | Telefon-Layout des aktiven Profils. Tippen auf eine Kachel öffnet ihr Detailblatt. |
| Reiterleiste | Wetter, Radar, Orte, Mehr. |
| Detailblatt | Von unten, mit Griff, schließt per Wischen nach unten oder Knopf. Volle Information der Kachel, Diagramme mit Finger abfahrbar. |
| Radar | Ganze Fläche: Karte mit Regenradar, Abspielleiste (gemessen und Vorhersage bis +2 h), Ebenen Warnungen und Blitze. |
| Orte | Liste mit aktueller Temperatur und Symbol, Ort wählen, Ort suchen und hinzufügen. Umsortieren und Löschen am Desktop. |
| Mehr | Profil wählen, Schriftstufe, Nachtbetrieb (Aus, Nach Sonnenuntergang, An), Zur Desktop-Ansicht, Hilfe, Fassung. |

Nach dem Ausrollen lädt die Ansicht von selbst neu wie am Desktop (`fassung.svelte.ts`). Ohne
Verbindung zeigt sie den letzten Stand je Ort mit Uhrzeit, der Frischepunkt wird gelb und nach einer
Stunde rot.

## Raster

- 3 quadratische Felder nebeneinander, beliebig viele Reihen. Feldgröße =
  (Bildschirmbreite - 2 Rand - 2 Fugen) / 3, bei 390 Punkten also 122.
- Rand und Fuge je 6 px, Eckenradius 14 px, Innenabstand 10 px.
- Kacheln von 1x1 bis 3x3 Feldern. Welche Größen ein Typ kann, steht im Katalog unten.
- Jede Kachel hat `x, y, w, h` und `conf`, wie am Desktop. Am Telefon werden die Werte nur gelesen
  und als CSS-Raster gesetzt (`grid-column`, `grid-row`), es läuft keine Rasterbibliothek.
- Der Editor am Desktop schiebt Kacheln nach oben zusammen, es entstehen keine Löcher.
- Die Größe des dicken Werts richtet sich nach der Kachel (Container-Abfragen `cqi`), nicht nach dem
  Bildschirm. Dadurch sieht dieselbe Kachel auf 375, 390 und 430 Punkten gleich aus.
- Nie läuft eine Kachel über. Jede Kachel kennt entbehrliche Inhalte (zum Beispiel die letzte
  Tageszeile oder eine Zusatzzeile), die bei großer Schrift oder kleinen Feldern zuerst wegfallen.
  Die Kachel misst dafür ihre Höhe selbst.

## Telefon-Kachelkatalog

Eigene Typen nur fürs Telefon, nicht die Desktop-Kacheln in klein. Jede Größe ist eine eigene,
gestaltete Form.

| Typ | Titel | Größen | Inhalt je Größe | Einstellungen | Daten |
|---|---|---|---|---|---|
| `jetzt` | Jetzt | 1x1, 2x1, 3x1, 2x2, 3x2 | 1x1 Temperatur, Symbol in der Ecke, gefühlt. 2x1 Symbol, Temperatur, Zustand, Hoch und Tief. 3x1 zusätzlich gefühlt. 2x2 Temperatur riesig, Zustand, gefühlt, Hoch und Tief. 3x2 zusätzlich Feuchte, Wind und Regen heute. | - | kompakt.jetzt, heute |
| `messwert` | Name des Werts | 1x1, 2x1, 3x1 | 1x1 Wert mit Einheit und kurzem Verlauf. 2x1 Wert links, Verlauf 24 h rechts, Tendenzpfeil. 3x1 Wert und Verlauf 7 Tage mit Tief und Hoch. | Wert: gefühlt, Feuchte, Taupunkt, Luftdruck, Sicht, Bewölkung, Regen heute, Böen | kompakt.jetzt, Archiv-Verlauf |
| `heute` | Heute | 2x1, 3x1 | Tagesspanne als Band mit Jetzt-Marke, Regen (Wahrscheinlichkeit und ab wann), Sonne (bis wann). | - | kompakt.heute |
| `stunden` | Stunden | 2x1, 3x1, 3x2, 3x3 | 2x1 4 Stunden. 3x1 6 Stunden mit Symbol, Temperatur, Regen. 3x2 12 Stunden: Verlauf mit Werten, Symbole, Regensäulen. 3x3 24 Stunden: zusätzlich Wind. | - | kompakt.stunden |
| `tage` | Tage | 1x1, 1x3, 2x2, 3x2, 3x3 | 1x1 morgen. 1x3 5 Tage schmal (Tag, Symbol, Hoch). 2x2 4 Tage ohne Band. 3x2 5 Tage mit Band. 3x3 7 Tage mit Band und Regen. | - | kompakt.tage |
| `regen` | Regen | 1x1, 2x1, 3x1 | Kurzfrist 2 h. 1x1 "in 25 Min" oder "trocken bis 17 Uhr". 2x1 Satz und Säulen. 3x1 zusätzlich Achse jetzt, +1 h, +2 h. | - | kompakt.regen |
| `wind` | Wind | 1x1, 2x1, 2x2 | 1x1 Wert und kleine Windrose. 2x1 Rose, Wert, Böen, Richtung. 2x2 große Rose, Wert, Böen, Stärke in Worten. | - | kompakt.jetzt |
| `uv` | UV | 1x1, 2x1 | 1x1 Bogen mit Wert und Wort. 2x1 Wert und Tageskurve mit Höchstwert und Uhrzeit. | - | kompakt.uv |
| `luft` | Luft | 1x1, 2x1, 2x2 | Index als Ring mit Wort. 2x1 dazu die zwei auffälligsten Schadstoffe. 2x2 vier Schadstoffe als Balken. | - | kompakt.luft |
| `pollen` | Pollen | 1x1, 2x1, 2x2, 1x3 | 1x1 stärkste Art mit Stufenpunkten. 2x1 zwei. 2x2 vier, gewählte Allergien zuerst. 1x3 bis sieben. | Allergien | kompakt.pollen |
| `sonne` | Sonne | 1x1, 2x1, 3x1 | 1x1 nächstes Ereignis mit kleinem Bogen. 2x1 Bogen mit Auf- und Untergang. 3x1 zusätzlich Tageslänge und Änderung zu gestern. | - | kompakt.sonne |
| `mond` | Mond | 1x1, 2x1 | 1x1 Scheibe und Anteil. 2x1 zusätzlich Phase, nächster Vollmond, Mondauf- und -untergang. | - | gerechnet |
| `warnungen` | Warnungen | 1x1, 3x1, 3x2 | 1x1 höchste Stufe und Anzahl. 3x1 oberste Warnung mit Zeit. 3x2 bis drei Warnungen. Ruhig "Keine Warnungen", bei Ausfall "Warnlage unbekannt". | - | kompakt.warnungen |
| `blitze` | Blitze | 1x1, 2x1, 2x2 | 1x1 Anzahl in 30 Min und nächster Abstand. 2x1 zusätzlich Richtung und zuletzt. 2x2 Entfernungsringe mit Einschlägen. | Umkreis | kompakt.blitze |
| `radar` | Regenradar | 2x2, 3x2, 3x3 | Kartenausschnitt um den Ort mit dem letzten gemessenen Radarbild und Uhrzeit. Tippen öffnet den Radar-Reiter. | - | Radarbild, Kartenkacheln |
| `monat` | Monatsvergleich | 2x1, 3x1, 3x2 | 2x1 Abweichung der Temperatur des laufenden Monats zum Klimamittel. 3x1 zusätzlich Abweichung je Monat. 3x2 zusätzlich Niederschlag zum Mittel. | - | Klima, Monatsaggregate |

Ohne eigene Telefonform bleiben Uhr und Kalender. Karte, Luftdruck, Temperaturverlauf, Klima und
Jahresmesswerte gehen in `radar`, `messwert` und `monat` auf.

### Vorlage für neue Profile

Jedes Profil bekommt beim ersten Öffnen am Telefon diese Vorlage (Profil "Zuhause" in
`mockups/telefon/wetter.html`):

| Kachel | x, y, w, h |
|---|---|
| jetzt | 0, 0, 2, 2 |
| regen | 2, 0, 1, 1 |
| wind | 2, 1, 1, 1 |
| stunden | 0, 2, 3, 1 |
| tage | 0, 3, 3, 2 |
| uv, luft, pollen | 0/1/2, 5, 1, 1 |
| sonne | 0, 6, 2, 1 |
| mond | 2, 6, 1, 1 |
| messwert Luftdruck | 0, 7, 2, 1 |
| messwert Feuchte | 2, 7, 1, 1 |
| radar | 0, 8, 3, 2 |
| monat | 0, 10, 3, 1 |

## Datenmodell

- Die Tabelle `layout` bekommt eine Spalte `telefon` (JSON): `{ "kacheln": [{ id, typ, x, y, w, h, conf }] }`.
  Ein Profil hat damit genau ein Desktop- und ein Telefon-Layout. Spaltenzahl 3 ist fest im
  Telefon-Katalog, nicht im Layout.
- Die Kachel-IDs sind UUIDs wie am Desktop.
- `PUT /layouts/{id}` nimmt `telefon` mit an. Das Backend prüft je Kachel Typ und Größe gegen den
  Telefon-Katalog (der Server erzwingt, was die Oberfläche anbietet).
- Fehlt `telefon`, liefert das Backend die Vorlage.
- Welches Profil ein Telefon zeigt, merkt sich das Gerät (lokaler Speicher). Ohne Wahl gilt das
  Startprofil. `?profil=` und `?ort=` in der Adresse gehen vor.

## Endpunkt für das Telefon

`GET /api/v1/wetter/kompakt/{ort}` mit festem Pydantic-Modell, rund 1,5 KB, gzip:

- `ort` mit Name und Zeitzone, `stand` je Bereich und `status` je Bereich (`ok`, `alt`, `fehlt`).
- `jetzt`: Temperatur mit Nachkomma, Wettercode, Tag oder Nacht, gefühlt, Feuchte, Taupunkt, Druck mit
  Tendenz, Sicht, Bewölkung, Wind, Böen, Richtung.
- `heute`: Hoch, Tief, Regenwahrscheinlichkeit, Regenbeginn, Sonnenauf- und -untergang (ISO 8601 mit Offset).
- `stunden` (24) und `tage` (7) als Spaltenlisten mit ISO-Zeit und Wettercode.
- `regen`: Beginn, Ende, Höchstwert mm/h, Säulen für 2 h, Quelle.
- `warnungen`: Liste mit Stufe, Ereignis, von, bis. Bei Ausfall `status: fehlt`, nie eine leere Liste.
- `blitze`: Anzahl 30 und 60 Minuten, nächster Abstand, Richtung, Zeit.
- `luft`: Index, Stufe, Schadstoffe. `pollen`: Arten mit Stufe heute und morgen.

Messwert-Verläufe für `messwert` holt die Kachel selbst über den Archiv-Verlauf (24 h stündlich, 7 Tage
täglich). Das Radarbild schneidet die Kachel im Client aus dem vorhandenen Deutschlandbild zu, die
Karte darunter kommt aus dem Kachelcache. In der Übersicht läuft keine Kartenbibliothek.

Takt: alle 5 Minuten, sofort beim Zurückkehren in die App. Blitze und Warnungen gehören in denselben
Abruf. Der letzte Stand je Ort liegt im lokalen Speicher und erscheint sofort beim Start.

## Aufbau im Frontend

```
frontend/
  index.html          Desktop-Einstieg
  telefon.html        Telefon-Einstieg (eigenes Bündel, ohne gridstack, MapLibre nur im Radar-Reiter)
  src/kern/           gemeinsam, ohne Oberfläche: api, datenquelle (mit Zustand laedt/fehlt/stand),
                      orte, fassung, uhr, zeit (Zeitzonen), format, rechnen (Mond, Sonne)
  src/desktop/        die heutige Oberfläche
  src/telefon/
    Telefon.svelte    Schale: Kopf, Warnband, Raster, Reiterleiste, Blätter
    Raster.svelte     setzt x, y, w, h als CSS-Raster
    katalog.ts        einzige Wahrheit der Telefon-Typen: Titel, Größen, Daten, Einstellungen,
                      Komponente und Detailblatt (beide nachgeladen)
    kacheln/          je Typ eine Komponente, bekommt w und h und wählt ihre Form
    mikro/            Linie, Saeulen, Bogen, Ring, Windrose, Sonnenbogen, Mond, Abweichung, Ringe
    blaetter/         Detailblätter je Typ
    ansichten/        Radar, Orte, Mehr
```

- Die Schale wird an genau einer Stelle gewählt: Ein kleines Skript im Kopf von `index.html` leitet
  Telefone (`pointer: coarse` und schmal) auf `/telefon` weiter und behält Ort und Profil. Die Wahl
  "Zur Desktop-Ansicht" merkt sich das Gerät. nginx liefert `/telefon` aus `telefon.html`.
- Die Mikrodiagramme sind kleine Svelte-Bausteine mit denselben Parametern wie `mockups/telefon/mikro.js`.

## Editor am Desktop

In der Layout-Verwaltung bekommt jedes Profil die Reiter **Desktop** und **Telefon**. Der Reiter
Telefon zeigt:

- links den Telefon-Katalog mit kleiner Vorschau je Größe zum Hineinziehen,
- in der Mitte einen Telefonrahmen mit den **echten** Telefon-Kacheln (dieselben Komponenten wie am
  Telefon, mit den Daten des aktiven Orts),
- rechts zur gewählten Kachel die Größenwahl (3x3-Gitter, nicht erlaubte Größen gesperrt),
  Einstellungen und Entfernen.

Ziehen und Größe ändern übernimmt gridstack mit 3 Spalten und quadratischen Feldern. Beim Loslassen
rastet die Größe auf die nächste erlaubte Form ein. Gespeichert wird nach jeder Änderung, wie am
Desktop.

## Voraussetzungen aus der Projektsichtung

Vor dem Bau der Telefonansicht, weil sie sonst dieselben Fehler erbt:

1. Platzhalterdaten aus dem Produktivpfad entfernen. Quellen bekommen Zustand und Stand.
2. Zeitstempel durchgehend mit Zeitzone (UTC in der Datenbank, Ortszeit in der Anzeige), Warnzeiten
   mit der Zeitzone des Orts.
3. Warnquelle mit Status: Ausfall darf nie wie "keine Warnungen" aussehen.
4. Desktop-Layouts vor dem 1-Spalten-Modus von gridstack schützen (bis zur Weiterleitung aufs Telefon).

## Umsetzungsschritte

1. Voraussetzungen (oben).
2. `kern/` herauslösen, Desktop unverändert lauffähig.
3. Endpunkt `kompakt` mit Modell und Tests.
4. Spalte `telefon`, Vorlage, Prüfung im Backend.
5. Telefon-Einstieg mit Schale, Raster, Reiterleiste, Mikrodiagrammen und den Kacheln der Vorlage.
6. Übrige Telefon-Typen und Detailblätter.
7. Radar-Reiter, Orte, Mehr, Nachtbetrieb, Schriftstufen, Offline-Stand.
8. Editor in der Layout-Verwaltung.
9. Weiterleitung für Telefone einschalten, am iPhone als PWA prüfen.

## Entwurfsseiten

| Seite | Zeigt |
|---|---|
| `telefon/wetter.html` | Übersicht, Profil Zuhause, ruhiger Tag |
| `telefon/unwetter.html` | Profil Unwetter: Warnung, Gewitter im Anzug |
| `telefon/kacheln.html` | Alle Telefon-Kacheltypen in allen Größen |
| `telefon/detail.html` | Detailblätter (Stunden, Tage, Regen, Wind, Jetzt) |
| `telefon/radar.html` | Radar-Reiter |
| `telefon/orte.html` | Orte |
| `telefon/mehr.html` | Mehr: Profil, Schrift, Nachtbetrieb |
| `telefon/nacht.html` | Nachtbetrieb |
| `telefon/zustaende.html` | Laden, ohne Verbindung, Quelle fehlt, Warnlage unbekannt |
| `telefon-editor.html` | Editor am Desktop |
