# Telefonansicht

Eigenständige Ansicht für das Telefon (iPhone als PWA vom Startbildschirm, ebenso andere Telefone),
erreichbar unter `/telefon`. Keine verkleinerte Desktop-Seite und keine Umbruchpunkte im
Desktop-Raster. Geteilt werden nur Daten, Endpunkte und Rechenkerne (`frontend/src/kern/`).
Bedienung, Gestaltung und Kacheln sind eigene.

Am Telefon wird **angezeigt**, nicht eingerichtet. Das Telefon-Layout gehört zum Profil und wird am
Desktop im **Telefon-Editor** bearbeitet (Navigation "Telefon-Layout", Adresse `/?ansicht=telefon`,
oder "Telefon einrichten" in der Layout-Verwaltung).

Entwürfe: `mockups/telefon/` (Galerie `mockups/index.html`, Abschnitt Telefon).

## Grundsätze

- Schwarzer Grund, Kacheln als dunkle Flächen ohne Rahmenlinien.
- Nachtbetrieb ausschließlich rot und gedämpft: kein Weiß, kein Blau, keine bunten Zustandsfarben.
  Zustände über Helligkeit und Form, Wettersymbole als einfarbige Masken, Karte über eine
  Multiplikationsfläche rot gefärbt (kein CSS-Filter).
- Grundschrift 17 px, kleine Texte 15 px, Kachelköpfe 13 px. Drei Schriftstufen (Normal, Groß,
  Sehr groß), je Gerät gespeichert. Alle Größen aus einer Skala von Variablen (`--s13` bis `--s26`).
- Nie läuft eine Kachel über: entbehrliche Inhalte (`entbehrlich`, `entbehrlich-gross`) fallen bei
  großer Schrift zuerst weg.
- Berührflächen ab 44 Punkten, nichts hängt am Überfahren.
- `display: standalone`, `viewport-fit=cover`, Sicherheitsbereiche über `env(safe-area-inset-*)`.
- Nie erfundene Werte: Was nicht geladen ist, zeigt einen ehrlichen Zustand (Laden, alt, fehlt).
  Ein Ausfall der Warnquelle zeigt "Warnlage unbekannt", nie "keine Warnungen".
- Die Seite rollt nie seitlich.

## Aufbau

| Bereich | Inhalt |
|---|---|
| Reiterleiste | **Karte**, **Wetter**, **Gesundheit**, **Mehr**. |
| Wischseiten | Karte, Wetter und Gesundheit in dieser Reihenfolge; Wetter ist die Startseite. Waagerecht wischen auf Wetter oder Gesundheit wechselt zur Nachbarseite. Auf der Karte wird gepannt, gewechselt wird dort über die Leiste. |
| Kopf (steht) | Ort mit Pfeil (Tippen öffnet die Orte als Blatt), Stand mit Frischepunkt (grün, gelb ab 15 Minuten, rot ab einer Stunde oder ohne Verbindung), Punkte der Orte. Wischen über dem Kopf wechselt den Ort. |
| Wetter | Kachelraster der Seite "wetter" des Profils. Darüber das Warnband, solange auf der Seite keine Warnkachel steht. |
| Gesundheit | Kachelraster der Seite "gesundheit": UV, Luft, Pollen, Messwerte. |
| Karte | Vollbild-Karte am Ort mit kleinen runden Symbolschaltern, jeder einzeln und unabhängig, je Gerät gemerkt: Gewitter (Blitze), Warnungen, Hell/Dunkel, Detailkarte (Beschriftung, Straßen), Regenradar (mit Abspielleiste gemessen bis +2 h), Wind. MapLibre wird erst hier geladen. |
| Detailblatt | Tippen auf eine Kachel öffnet ihr Blatt von unten (Griff, nach unten ziehen schließt). Die Kachel zeigt nur das Wesentliche, das Blatt alles. Die Regenradar-Kachel öffnet die Karte. |
| Mehr | Profil wählen, Schriftstufe, Nachtbetrieb, alle Kachelformen ansehen, Fassung und Quellen. |

**Nachtbetrieb:** Standard ist "Nach Sonnenuntergang": zwischen Sonnenuntergang und -aufgang am
gewählten Ort. Wählbar außerdem "Aus" und "An". Der Mond- bzw. Sonnenknopf im Kopf (und auf der Karte)
schaltet jederzeit von Hand um; bei Zeitsteuerung gilt das bis zum nächsten Sonnenauf- oder -untergang,
danach übernimmt wieder die Automatik (Hinweis unter Mehr).

Nach dem Ausrollen lädt die Ansicht von selbst neu wie am Desktop (`kern/fassung.svelte.ts`), aber nur,
wenn der Server unmittelbar davor antwortet; ohne Verbindung bleibt die laufende Fassung stehen. Die App-
Schale wird nie zwischengespeichert, nur Daten. Ohne Verbindung zeigt sie den letzten Stand je Ort aus
dem Gerätespeicher mit Uhrzeit. Die Kartenbibliothek lädt erst der Karten-Reiter; ohne Verbindung steht
dort ein Hinweis, und die Seite lädt neu, sobald der Server wieder antwortet.

**Weiche:** `index.html` leitet Telefone (Touch und kürzere Bildschirmseite unter 600 Punkten) auf
`/telefon` weiter, Ort und Profil bleiben in der Adresse. Am Telefon gibt es nur diese Ansicht, die
Desktop-Ansicht ist dort nicht wählbar (Nutzer 30.10.2026). Eigenes Manifest `telefon.webmanifest` (Start `/telefon`, schwarz).

## Raster

- 3 quadratische Felder nebeneinander, beliebig viele Reihen. Feld = (Bildschirmbreite - 2 Rand -
  2 Fugen) / 3, bei 390 Punkten also 122. Rand und Fuge je 6 px, Radius 14 px.
- Kacheln von 1x1 bis 3x3 Feldern; welche Größen ein Typ kann, steht im Katalog.
- Jede Kachel hat `id, typ, x, y, w, h, conf`. Am Telefon nur gelesen und als CSS-Raster gesetzt.
- Der dicke Wert richtet sich nach der Kachel (Container-Einheiten), nicht nach dem Bildschirm.

## Gemeinsame Dateien (`gemeinsam/`)

Einzige Wahrheit für Backend und Oberfläche, beim Bau in die Oberfläche eingebaut (`vite.config.ts`),
vom Backend gelesen (`backend/src/wetterwarte/gemeinsam.py`):

- `telefon-katalog.json`: Seiten, Familien, Kacheltypen (Titel, Symbol, Beschreibung, erlaubte
  Größen, erlaubte Seiten, Einstellungen), allgemeine Vorlage je Seite, Vorlagen je Profilname
  (Unwetter, Garten, Reise).
- `wettercodes.json`: WMO-Wettercode zu Wettersymbol (Tag, Nacht) und Text.

## Telefon-Kachelkatalog

| Typ | Seiten | Größen | Inhalt |
|---|---|---|---|
| `jetzt` | Wetter | 1x1, 2x1, 3x1, 2x2, 3x2 | Temperatur, Zustand, gefühlt, Hoch und Tief; 3x2 mit Feuchte, Wind, Regen. |
| `messwert` | beide | 1x1, 2x1, 3x1 | Ein Wert (gefühlt, Feuchte, Taupunkt, Luftdruck, Sicht, Bewölkung, Regen heute, Böen) mit Verlauf 24 h bzw. 48 h aus den Stundenwerten. |
| `heute` | Wetter | 2x1, 3x1 | Tagesspanne mit Jetzt-Marke, Regen ab wann, Sonne bis wann. |
| `stunden` | Wetter | 2x1, 3x1, 3x2, 3x3 | 4, 6, 12 oder 24 Stunden; ab 3x2 als Verlauf mit Regensäulen, 3x3 mit Wind. |
| `tage` | Wetter | 1x1, 1x3, 2x2, 3x2, 3x3 | morgen, 5 schmal, 4, 5 mit Band, 7 mit Band und Regen. |
| `regen` | Wetter | 1x1, 2x1, 3x1 | Kurzfrist 2 h: "trocken bis", "Regen in", Säulen. |
| `wind` | Wetter | 1x1, 2x1, 2x2 | Windrose, Wert, Böen, Richtung, Stärke in Worten. |
| `uv` | Gesundheit | 1x1, 2x1, 3x1, 2x2 | Bogen mit Wert und Wort, Tageskurve mit Höchstwert. |
| `luft` | Gesundheit | 1x1, 2x1, 2x2, 3x1, 3x2 | Index als Ring, Schadstoffe als Balken. |
| `pollen` | Gesundheit | 1x1, 2x1, 2x2, 1x3, 3x2, 3x3 | Gewählte Allergien zuerst, Stufenpunkte, ab 3x2 heute und morgen. |
| `sonne` | beide | 1x1, 2x1, 3x1 | Nächstes Ereignis, Bogen, Tageslänge und Änderung zu morgen. |
| `mond` | Wetter | 1x1, 2x1 | Scheibe, Anteil, Phase, Vollmond in Tagen. |
| `warnungen` | Wetter | 1x1, 2x1, 3x1, 3x2 | 1x1 nur Stufe und Anzahl (Tippen zeigt alles), 2x1 mit Ereignis, 3x1 oberste Warnung, 3x2 bis drei. |
| `blitze` | Wetter | 1x1, 2x1, 2x2 | Anzahl, nächster Abstand, Richtung, Ringe; Umkreis einstellbar. |
| `radar` | Wetter | 2x2, 3x2, 3x3 | Kartenausschnitt mit dem letzten gemessenen Radarbild, ohne Kartenbibliothek. |
| `monat` | Wetter | 2x1, 3x1, 3x2 | Laufender Monat gegen das Klimamittel, Abweichung je Monat. |

Der Schaukasten unter Mehr ("Alle Kachelformen", auch `/telefon?blatt=schaukasten`) zeigt jeden Typ in
jeder Größe mit den echten Daten des Orts.

## Datenmodell

- `layout.telefon` (JSON): `{ "seiten": { "wetter": [Kachel], "gesundheit": [Kachel] } }`.
- `PUT /layouts/{id}` nimmt `telefon` mit an. Das Backend prüft Typ, Seite, Größe, Lage, Einstellungen,
  Überlappung und doppelte IDs gegen den Katalog (`telefon.py`), Ablehnung mit 422 und Grund.
- Neue Profile und `POST /layouts/{id}/telefon-vorlage` bekommen die Vorlage, Standardprofile ihre
  eigene. Beim Start bekommen Profile ohne Telefon-Layout die Vorlage (`migrationen.py`).
- Welches Profil ein Telefon zeigt, merkt sich das Gerät; `?profil=` und `?ort=` gehen vor.

## Endpunkt

`GET /api/v1/wetter/kompakt/{ort}` (Modell `schemas/kompakt.py`, rund 3 KB komprimiert): Ort mit
Zeitzone, Status und Stand je Bereich, `jetzt`, `stunden` (6 zurück bis 48 voraus, `jetzt_index`),
`tage` (7), `regen` (2 h in Viertelstunden), `warnungen` (null bei Ausfall), `blitze` (mit Einschlägen),
`luft`, `pollen`. Zahlen ungerundet, Zeiten ISO 8601 mit Versatz. Abruf alle 5 Minuten und beim
Zurückkehren in die App; letzter Stand je Ort im Gerätespeicher.

Die Monatskachel holt `/wetter/klima/{ort}` und `/wetter/jahresmesswerte/{ort}`, Regenradar-Kachel und
Karte `/radar/rahmen` und `/radar/bild/{id}.png`, die Karte zusätzlich Warnpolygone, Kartengitter und
Blitze wie am Desktop.

## Aufbau im Frontend

```
frontend/
  index.html            Desktop-Einstieg (mit Weiche für Telefone)
  telefon.html          Telefon-Einstieg, eigenes Bündel (kein gridstack, MapLibre nur im Karten-Reiter)
  src/kern/             gemeinsam: api, datenquelle, orte, fassung, uhr, zeit, mond, kennung,
                        gemeinsam (Katalog, Wettercodes), wetterbild, icons, speicher, begriffe
  src/telefon/
    Telefon.svelte      Wurzel: Seiten, Reiterleiste, Blätter, data-stufe und data-modus
    Seite.svelte        Kachelseite (Kopf, Warnband, Raster), wischt zur Nachbarseite
    Kachel.svelte       Hülle: Lage, Tippen, Laden, Ausfall, Altersmarke
    katalog.ts          Komponente, Detailblatt und Datenbereiche je Typ
    kacheln/  blaetter/  mikro/  ansichten/ (Karte, Orte, Mehr)
    meldungen/          Gerät beim Server (konto.svelte.ts) und Web Push (push.ts), siehe WARNUNGEN.md
    ansagen/            Tonansagen: Spieler (Web Audio), Abholen im Takt, Untertitel, klaenge/*.mp3
    telefon.css         Gestaltungssystem; jede Regel unter .tel, damit der Editor sie einbinden kann
  src/lib/telefoneditor/  Editor am Desktop (Rasterlogik raster.ts, Zustand editor.svelte.ts)
```

## Meldungen und Was kommt

Aktive Warnungen ([WARNUNGEN.md](WARNUNGEN.md)) haben am Telefon drei Orte:

- **Lageband** auf der Wetterseite: ohne amtliche Warnung steht dort das nächste Ereignis der Lage
  ("Leichter Regen in 30 Minuten"), ruhig bis Stufe 2, ab Stufe 3 in Warnfarbe. Tippen öffnet "Was kommt".
- **Blatt "Was kommt"** (`?blatt=lage`): alle kommenden Ereignisse mit Text, Beginn und Quelle, laufende
  darunter, zuletzt Gemeldetes. Hierher führt das Antippen einer Mitteilung; amtliche Warnungen öffnen das
  Blatt Warnungen.
- **Blatt "Meldungen"** (Mehr, `?blatt=meldungen`): Mitteilungen ein und aus mit Probe, Orte, Tonansagen
  mit Probeansage, Arten, Stärke, Vorlauf und Nachtruhe. Ohne HTTPS oder auf dem iPhone außerhalb der App
  vom Home-Bildschirm erklärt das Blatt, was fehlt, statt einen toten Schalter zu zeigen.

Während eine Ansage läuft, steht ihr Text als Untertitel über der Reiterleiste; Tippen beendet sie.

## Editor am Desktop

- Oben Profil, Seite (Wetter, Gesundheit), Vorschau-Ort, Breite (375, 390, 430), Tag oder Nacht,
  "Vorlage wiederherstellen" (zweimal klicken).
- Links der Katalog der Seite mit Größenzeichen und Anzahl im Profil; Klick fügt am ersten freien
  Platz ein.
- Mitte ein Telefonrahmen mit den echten Telefon-Kacheln und den Daten des Vorschau-Orts. Ziehen auf
  ein Feld verschiebt: die gezogene Kachel bekommt ihren Platz, was im Weg ist, weicht nach unten
  aus, die Reihenfolge bleibt, leere Reihen fallen weg.
- Rechts die gewählte Kachel: Größenwahl als 3x3-Gitter (nicht erlaubte gesperrt), Einstellungen,
  Entfernen (zweimal klicken). Jede Änderung wird sofort gespeichert.
