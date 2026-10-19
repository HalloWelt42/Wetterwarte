# Aktive Warnungen: Meldungen aufs Telefon und Tonansagen

Die Wetterwarte meldet von sich aus, was kommt: amtliche Warnungen, Regen und Schnee, Gewitter und Sturm.
Zwei Wege tragen dieselbe Meldung: eine **Mitteilung aufs Telefon** (Web Push, auch bei geschlossener App) und
eine **Tonansage** mit der Zeit-Stimme, solange die App offen ist. Regen meldet sie gestaffelt, von mehreren
Stunden vorher bis 15 Minuten vor dem Eintreffen, und jedes Mal mit dem neuesten Stand.

## Entscheidungen des Nutzers (19.10.2026)

- Mitteilungen aufs iPhone: über die sichere Adresse (HTTPS mit dem Zertifikat der Hausstelle), die App wird von
  dort zum Home-Bildschirm hinzugefügt.
- Orte je Gerät wählbar, vorgewählt ist der Startort des Geräts.
- Nachtruhe 22 bis 7 Uhr: dann kommen nur Unwetter ab Stufe 3 durch. Zeiten unter Mehr änderbar.
- Tonansagen bei offener App, immer mit der Zeit-Stimme, vorab vertont: Zahlenräume als ganze Sätze
  vorgeneriert und je Lage zusammengesetzt wie im Spiel Orbit, abgelegt als MP3.

## Überblick

```
Quellen (Bereiche, bereiche.py)          lage.py (rein)            melden.py (rein)            Kanäle
basis (Open-Meteo, 15 min + Stunden) ┐
nowcast (DWD-Radar RADVOR, 5 min)    ├─> Ereignisse je Ort  ──>  Buchführung je Gerät  ──┬─> melder.py: Web Push
warnungen (DWD)                      │   (Art, Stufe, Beginn,     und Kanal: was ist neu,  │   (Hintergrund, alle 5 min)
blitze (Blitzdienst)                 ┘    Vorlaufstufe, Sätze)    was entfällt              └─> POST /geraete/{id}/ansagen
                                                                                                 (App offen, spricht)
```

- **Eine Wahrheit je Sache.** Was eine Lage ist, entscheidet nur `lage.py`; was neu zu melden ist, nur
  `melden.py`. Push und Ansage nutzen beide, jeder Kanal führt sein eigenes Gedächtnis.
- **Text und Ton aus einem Katalog.** `gemeinsam/meldungen.json` nennt jeden Satz einmal, dazu Arten, Klassen, Schwellen, Vorlaufstufen und die Einstellmöglichkeiten der Geräte. Das Backend setzt eine
  Meldung aus Satzschlüsseln zusammen; der Mitteilungstext ist die Verkettung ihrer Texte, die Ansage spielt
  dieselben Schlüssel als Klänge. Was gesprochen wird, steht also wörtlich in der Mitteilung.
- **Der Pi rechnet keine Stimmen.** Vertont wird einmal auf dem Mac (Medienpool, Zeit-Stimme), die MP3-Dateien
  liegen im Repo und kommen mit der Oberfläche.

## Lage: Ereignisse je Ort (`backend/src/wetterwarte/lage.py`)

Ein Ereignis hat: Art, Episodenschlüssel, Klasse (mit Rang innerhalb der Art), Stufe 1 bis 4 nach dem Maßstab
der amtlichen Warnstufen (3 = Unwetter), Beginn, ob es schon läuft, Vorlauf in Minuten, die Vorlaufstufe, Titel,
Satzschlüssel und Text. Die Stufe macht alle Arten vergleichbar, darum gilt die Nachtregel "ab Stufe 3" für alle.

| Art | Quelle | Klassen (Rang aufsteigend) | Stufe |
|---|---|---|---|
| Niederschlag | Radar-Nowcast bis 2 h (5 min), danach Modell (15 min bis 4 h, dann Stunden bis 6 h) | Regen leicht (< 2,5 mm/h), Regen (bis 10), Regen stark (bis 25), Regen sehr stark (ab 25); Schnee leicht, Schnee, Schnee stark; gefrierender Regen | aus der Regenrate wie beim Wetterdienst (Starkregen ab 15 mm/h Stufe 2, ab 25 Stufe 3, ab 40 Stufe 4), gefrierender Regen Stufe 3 |
| Gewitter | Modell (Wettercode 95, 96, 99) bis 6 h | Gewitter, Gewitter mit Hagel | 2, mit Hagel 3 |
| Blitze | Blitzdienst, letzte 15 Minuten, bis 30 km | Entfernung 30, 20, 10, 5 km (näher = höherer Rang) | 1 bis 3 |
| Wind | Modell (Böen) bis 12 h | stürmische Böen (ab 65 km/h), Sturmböen (75), schwere Sturmböen (89), orkanartige Böen (103), Orkanböen (118) | 2, 2, 3, 3, 4 |
| Amtliche Warnung | Deutscher Wetterdienst | Ereignis der Warnung | Warnstufe |

Regeln, die für alle gelten:

- **Episode.** Je Art gibt es höchstens eine kommende Episode (die nächste). Niederschlag zählt erst als Episode,
  wenn es mindestens 15 Minuten am Stück nass ist (ab 0,2 mm/h), damit ein einzelner Radarpunkt nicht meldet.
- **Radar vor Modell.** Liegt der Ort im Radargebiet und ist der Nowcast frisch, gilt er für die ersten zwei
  Stunden, auch wenn das Modell anderes sagt. Ohne Radar (Ausland, Ausfall) zählt nur das Modell.
- **Läuft schon.** Regnet es gerade, ist die Episode "laufend" und wird nicht angekündigt; danach beginnt die
  nächste Episode neu.
- **Vorlaufstufen.** Niederschlag 360, 180, 120, 60, 30, 15 Minuten; Gewitter 180, 60, 15; Wind 360, 120, 30.
  Der Vorlauf eines Geräts (1, 2, 3 oder 6 Stunden) begrenzt, ab wann gemeldet wird.
- **Radar-Einheit.** RADOLAN RY und RADVOR RV liefern Niederschlagshöhe je 5 Minuten (0,01 mm); die Wetterwarte
  rechnet sie beim Dekodieren in mm/h um (Intervall aus dem Kopf der Datei).

## Buchführung: was neu zu melden ist (`backend/src/wetterwarte/melden.py`)

Je Gerät, Kanal (push, ansage), Ort und Episodenschlüssel steht der zuletzt gemeldete Zustand (Rang,
Vorlaufstufe, Beginn, läuft). Gemeldet wird, wenn

1. eine Episode neu ist und das Gerät ihre Art, Klasse und Vorlaufstufe will,
2. ihre Vorlaufstufe dringlicher geworden ist (etwa von 60 auf 30 Minuten) oder
3. ihre Klasse stärker geworden ist (leichter Regen wird starker Regen, Blitze kommen näher).

Rückt der Beginn mindestens zwei Vorlaufstufen nach hinten, merkt sich die Buchführung still die neue Stufe:
beim nächsten Näherkommen meldet sie wieder. Verschwindet eine gemeldete Episode, deren Beginn noch mehr als
zehn Minuten entfernt war, kommt eine **Entwarnung** ("Der angekündigte Regen bleibt aus."). Amtliche Warnungen
werden einmal gemeldet, wenn sie erscheinen; eine höhere Stufe ist beim Wetterdienst eine neue Warnung.

**Nachtruhe** (nur Push): in der eingestellten Zeit, in Ortszeit des gemeldeten Orts, kommen nur Ereignisse ab
Stufe 3. Unterdrückte Meldungen verändern das Gedächtnis nicht; am Morgen kommt also der dann aktuelle Stand.

## Geräte und Einstellungen

Ein Gerät ist ein Eintrag in der Datenbank (Kennung als UUID vom Server, im Gerätespeicher gemerkt), weil der
Server auch bei geschlossener App wissen muss, was es will. Einstellungen je Gerät:

- Orte für Mitteilungen (vorgewählt: der Startort beim Einschalten), Arten (amtliche Warnungen, Niederschlag,
  Gewitter, Wind), Niederschlag ab (alles, ab mäßig, nur stark), Wind ab (65, 75 oder 89 km/h), Vorlauf
  (1, 2, 3, 6 Stunden), Nachtruhe (an/aus, von, bis in vollen Stunden).
- Ein Push-Abo (Endpunkt und Schlüssel des Browsers) oder keins; Tonansagen schaltet das Gerät selbst (sie
  brauchen den Server nur zum Abholen).

API unter `/api/v1`:

| Weg | Zweck |
|---|---|
| `GET /push/schluessel` | öffentlicher VAPID-Schlüssel (entsteht beim ersten Start, liegt in `einstellung`) |
| `POST /geraete` | Gerät anlegen (Startort), liefert Kennung und Einstellungen |
| `GET /geraete/{id}` | Einstellungen, ob ein Push-Abo besteht, letzte Mitteilungen |
| `PUT /geraete/{id}/einstellungen` | Einstellungen setzen |
| `PUT /geraete/{id}/push`, `DELETE /geraete/{id}/push` | Push-Abo hinterlegen oder löschen |
| `POST /geraete/{id}/probe` | Probemitteilung senden |
| `POST /geraete/{id}/ansagen?ort=` | neue Ansagen für den gezeigten Ort abholen (die App spricht sie) |
| `DELETE /geraete/{id}` | Gerät vergessen |

Abgelaufene Abos (Antwort 404 oder 410 des Push-Dienstes) löscht der Melder. Jede gesendete Mitteilung steht im
Protokoll (`meldung`), die letzten zeigt das Telefon unter Mehr.

## Ansagekatalog (`gemeinsam/meldungen.json`, Abschnitt `ansagen`)

- **Kernsätze als Zahlenreihen.** Je Klasse ein Muster mit `{zeit}`, vorgeneriert für alle Zeiten der Liste
  (in wenigen Minuten, 15, 30, 45 Minuten, einer Stunde, anderthalb, 2, zweieinhalb, 3, 4, 5, 6 Stunden):
  "Es wird in deiner Region in 3 Stunden leicht regnen." So klingt jeder Satz wie gesprochen, nicht geschnitten.
- **Zusätze als Reihen.** Spitzenböen bis n km/h, Gewitter etwa n Kilometer entfernt, ab/bis n Uhr (auch
  morgen).
- **Amtliche Warnungen** aus Einleitung je Stufe, Ereignisname (Liste der Ereignisse des Wetterdienstes; ein
  unbekanntes Ereignis bekommt "Die Einzelheiten stehen in der Wetterwarte.") und Zeitraum.
- **Feste Sätze**: Entwarnungen je Art, Probeansage.

Vertonung: `tools/ansagen.py` gleicht alle Schlüssel mit dem Medienpool ab (Projekt `wetterwarte`, Rolle Zeit
mit der Zeit-Stimme, ohne Effekte), startet die Vertonung, füllt den Satz und exportiert ihn als MP3 nach
`frontend/src/telefon/ansagen/klaenge/`. Fehlt ein Klang, spricht die App die übrigen Bausteine; der Text der
Mitteilung ist immer vollständig.

Abspielen (`frontend/src/telefon/ansagen/`): ein Gong (Web Audio, nach Stufe), dann die Bausteine mit kurzer
Pause. Auf dem iPhone braucht Ton eine Berührung zum Freischalten; das geschieht beim Einschalten der Ansagen
und bei jeder Berührung der App. Mehrere Ansagen auf einmal laufen nacheinander, höchste Stufe zuerst.

## Sichere Adresse (HTTPS)

Web Push und Service Worker gibt es nur in einem sicheren Kontext. Vor dem Frontend steht ein Caddy
(`vorne`, Port 8062) mit dem Blattzertifikat der Hausstelle (mkcert auf dem Mac, wie Kiste, Kellerwolke und
Transkription); die bisherige Adresse auf 8061 bleibt. Ausstellen und Kopieren: `./wetter zertifikat`. Auf dem
iPhone: `https://<Pi>:8062/telefon` öffnen, Teilen, Zum Home-Bildschirm, aus dem neuen Symbol starten, unter Mehr
Mitteilungen einschalten.

Der Service Worker (`public/sw.js`) zeigt nur Mitteilungen und öffnet beim Antippen den Ort mit dem passenden
Blatt. Er hat keinen fetch-Handler: zwischengespeichert wird nichts, die App lädt nach jedem Ausrollen frisch.
