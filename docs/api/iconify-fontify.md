# Iconify und Fontify - lokale Icons und Schriften

Zwei selbst gehostete Dienste auf dem Pi, die Icons (Iconify) und Webschriften (Fontify) ohne fremdes CDN bereitstellen. Die Wetterwarte bindet darüber alle SVG-Icons und die Schrift Barlow direkt vom eigenen Server ein, damit die App vollständig unabhängig und offline lauffähig bleibt.

Beide Dienste laufen auf demselben Rechner (Pi unter `192.168.178.49`). Aufrufe erfolgen per HTTP GET, es wird kein Schlüssel benötigt. Beide bieten unter `/health` eine Statusabfrage und unter `/docs` bzw. `/openapi.json` eine maschinenlesbare Beschreibung.

---

# Teil 1: Iconify (Icons)

Liefert SVG-Icons aus mehreren freien Icon-Sets, entweder als fertige SVG-Datei oder als durchsuchbaren Katalog. Version zum Zeitpunkt dieser Doku: 3.0.0.

## Basis-URL

```
http://192.168.178.49:8766
```

## Verfügbare Icon-Sets

Die installierten Sets fragt man über `/api/sets` ab. Aktuell vorhanden (Stil-Angaben sind wichtig, weil sie im direkten Pfad als Segment auftauchen):

| Set-ID | Name | Stile (`style`) | Icons | Lizenz |
|---|---|---|---|---|
| `material-symbols` | Material Symbols | `outlined`, `rounded`, `sharp` | 7782 | Apache 2.0 |
| `mdi` | Material Design Icons | `default` | 7447 | Apache 2.0 |
| `phosphor` | Phosphor | `regular`, `bold`, `fill`, `light`, `thin`, `duotone` | 9072 | MIT |
| `tabler` | Tabler Icons | `outline`, `filled` | 5093 | MIT |
| `remix` | Remix Icon | `default` (nach Kategorie sortiert) | 3229 | Apache 2.0 |
| `bootstrap` | Bootstrap Icons | `default` | 2078 | MIT |
| `fontawesome` | Font Awesome Free | `solid`, `regular`, `brands` | 1895 | CC BY 4.0 (Namensnennung nötig) |
| `lucide` | Lucide | `default` | 1713 | MIT |
| `heroicons` | Heroicons | `24/outline`, `24/solid`, `20/solid`, `16/solid` | 324 | MIT |
| `feather` | Feather Icons | `default` | 287 | MIT |

Wichtige Antwortfelder je Set: `id`, `name`, `styles` (Liste der verfügbaren Stile), `icon_count`, `has_font` (ob eine Icon-Schrift existiert), `license`, `license_category` (`permissive`, `attribution`), `requires_attribution` (ob eine Namensnennung nötig ist).

### Set-Liste abrufen

`GET /api/sets` - optionaler Parameter `license_category` filtert nach Lizenzart (z. B. `permissive`).

```bash
curl "http://192.168.178.49:8766/api/sets?license_category=permissive"
```

```json
[
  {
    "id": "material-symbols",
    "name": "Material Symbols",
    "styles": ["outlined", "rounded", "sharp"],
    "icon_count": 7782,
    "has_font": true,
    "license": "Apache 2.0",
    "license_category": "permissive",
    "requires_attribution": false
  }
]
```

Ein einzelnes Set liefert `GET /api/sets/{set_id}` mit zusätzlichen Feldern wie `font_family`, `font_class_pattern` und `font_url`.

## Ein einzelnes Icon holen

Für das Einbetten in die Wetterwarte gibt es zwei Wege. Empfohlen ist der API-Weg, weil er den Stil automatisch auflöst.

### Weg A (empfohlen): API-Endpunkt

`GET /api/icons/{set_id}/{icon_name}/svg`

Parameter:

- `set_id` (Pfad, Pflicht) - z. B. `material-symbols`
- `icon_name` (Pfad, Pflicht) - z. B. `home`
- `style` (Query, optional) - gewünschter Stil, z. B. `rounded`. Ohne Angabe wird der erste Stil des Sets verwendet.

Antwort: die rohe SVG-Datei mit `Content-Type: image/svg+xml`.

```bash
curl "http://192.168.178.49:8766/api/icons/material-symbols/home/svg?style=rounded"
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960"><path d="M220-180h150v-250h220v250h150v-390L480-765 220-570v390Z"/></svg>
```

### Weg B: direkter Datei-Pfad (statisch)

Der Dienst legt jedes Icon zusätzlich als statische Datei ab und liefert sie direkt aus. Der Pfad spiegelt den Aufbau auf der Platte:

- Sets mit nur einem Stil (`default`): `GET /icons/{set_id}/{icon_name}.svg`
  - Beispiel: `http://192.168.178.49:8766/icons/mdi/home.svg`
- Sets mit mehreren Stilen oder Kategorien: `GET /icons/{set_id}/{style}/{icon_name}.svg`
  - Beispiel: `http://192.168.178.49:8766/icons/material-symbols/rounded/home.svg`
  - Beispiel: `http://192.168.178.49:8766/icons/fontawesome/solid/house.svg`

Achtung: Beim direkten Pfad muss der Stil-Ordner exakt stimmen, sonst kommt `404`. Ein Aufruf ohne Stil-Segment (`/icons/material-symbols/home.svg`) schlägt bei Mehr-Stil-Sets fehl. Den genau passenden Pfad liefert die Suche im Feld `path` (siehe unten) - dort allerdings ohne die Endung `.svg`, die man beim direkten Abruf anhängen muss.

Wenn man den Stil nicht kennt, ist Weg A robuster.

### Icon-Code und fertige Einbettungs-Schnipsel

`GET /api/icons/{set_id}/{icon_name}/code`

Liefert nicht nur das SVG, sondern gleich mehrere fertige Code-Varianten als JSON.

Parameter:

- `set_id`, `icon_name` (Pfad, Pflicht)
- `style` (Query, optional)
- `color` (Query, optional) - Vordergrundfarbe als Hex, Standard `#000000`
- `size` (Query, optional) - Kantenlänge in Pixel, Standard `24`

```bash
curl "http://192.168.178.49:8766/api/icons/mdi/home/code?color=%23ff0000&size=32"
```

```json
{
  "svg": "<svg width=\"32\" height=\"32\" ... viewBox=\"0 0 24 24\"><path d=\"M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z\" /></svg>",
  "img": "<img src=\"/icons/mdi/home.svg\" width=\"32\" height=\"32\" alt=\"home\">",
  "font_html": "<i class=\"mdi mdi-home\" style=\"font-size: 32px; color: #ff0000;\"></i>",
  "has_font": true,
  "license": "Apache 2.0"
}
```

Wichtige Antwortfelder: `svg` (SVG-Text mit gesetzter Größe), `img` (fertiges `<img>`-Tag auf den statischen Pfad), `font_html` und `font_css` (nur falls `has_font` true), `font_url`, `has_font`, `license`.

Hinweis zur Farbe: Der Parameter `color` steuert vor allem die Schrift-Variante (`font_html`). Der reine SVG-Inhalt behält die Farbgebung des jeweiligen Sets - Umriss-Sets (z. B. `lucide`, `feather`, `heroicons/*/outline`) nutzen `currentColor` und lassen sich per CSS-`color` einfärben, Flächen-Sets (z. B. `material-symbols`) haben eine feste Füllung. Zum sicheren Umfärben das SVG inline einbetten und `fill` bzw. `color` per CSS setzen.

## Icons durchsuchen

`GET /api/icons/search`

Parameter:

- `q` (Query, optional) - Suchbegriff (englische Icon-Namen)
- `set_id` (Query, optional) - Suche auf ein Set eingrenzen
- `style` (Query, optional) - auf einen Stil eingrenzen
- `scope` (Query, optional) - `all` (alle Sets), `set` (aktuelles Set), `custom` (eigene Sets). Standard `set`
- `license` (Query, optional) - Lizenzfilter
- `page` (Query, optional) - Seitenzahl, Standard `1`
- `per_page` (Query, optional) - Treffer je Seite, Standard `120`, Minimum `10`

```bash
curl "http://192.168.178.49:8766/api/icons/search?q=cloud&scope=all&per_page=10&page=1"
```

```json
{
  "icons": [
    { "name": "cloud", "style": "outlined", "path": "/icons/material-symbols/outlined/cloud", "set_id": "material-symbols" }
  ],
  "total": 365,
  "page": 1,
  "per_page": 10,
  "pages": 37
}
```

Wichtige Antwortfelder: `icons` (Liste mit je `name`, `style`, `set_id` und `path`), `total` (Gesamttreffer), `page`, `per_page`, `pages` (Seitenanzahl). Das Feld `path` zeigt auf den statischen Pfad ohne die Endung `.svg` - zum direkten Laden `.svg` anhängen.

### KI-gestützte Suche (optional)

`GET /api/icons/ai-search` sucht per natürlicher Sprache statt exakter Stichworte (Parameter `q`, `scope` mit Standard `all`, `license`, `per_page`). Sie benötigt einen konfigurierten LM-Studio-Zugang (siehe `/api/llm/config`) und ist für die Wetterwarte nicht erforderlich.

## Weitere Endpunkte (Kurzreferenz)

Diese Endpunkte werden für das reine Einbetten von Icons nicht gebraucht, runden das Bild aber ab:

| Methode und Pfad | Zweck |
|---|---|
| `GET /health` | Statusabfrage, Antwort `{"status":"healthy","version":"3.0.0"}` |
| `POST /api/sets/{set_id}/download` | Ein Set nachladen |
| `GET /api/sets/{set_id}/progress` | Download-Fortschritt eines Sets |
| `DELETE /api/sets/{set_id}` | Ein Set entfernen |
| `GET /api/custom/sets` | Eigene, kuratierte Sets auflisten |
| `POST /api/custom/sets` | Eigenes Set anlegen |
| `POST /api/custom/sets/{set_id}/icons` | Icons in ein eigenes Set hochladen |
| `POST /api/custom/sets/{set_id}/icons/from` | Icon aus einem anderen Set übernehmen |
| `POST /api/export/sprite` | Ausgewählte Icons als SVG-Sprite exportieren |
| `POST /api/export/zip` | Ausgewählte Icons als ZIP exportieren |
| `POST /api/font/generate` | Aus Icons eine Icon-Schrift erzeugen |
| `GET /api/font/download/{filename}` | Erzeugte Icon-Schrift herunterladen |
| `GET /api/llm/config`, `PUT /api/llm/config`, `POST /api/llm/test` | LM-Studio-Zugang für die KI-Suche verwalten |

## Grenzen, Aktualisierung und Frische (Iconify)

- Die SVG-Dateien sind statisch: Sie ändern sich nur, wenn ein Set nachgeladen oder aktualisiert wird. Der Inhalt eines Icons ist damit dauerhaft stabil und kann bedenkenlos zwischengespeichert werden.
- `per_page` bei der Suche akzeptiert keine Werte unter 10, sonst antwortet der Dienst mit `422` (Validierungsfehler).
- Icon-Namen sind englisch und setzweise unterschiedlich (z. B. `home` bei Material Symbols und MDI, aber `house` bei Font Awesome). Bei Unsicherheit erst über die Suche den genauen Namen und Stil ermitteln.
- Font Awesome verlangt laut Lizenz eine Namensnennung (`requires_attribution` true). Für die eigenen Zwecke der Wetterwarte am besten Sets mit `license_category: permissive` bevorzugen.

---

# Teil 2: Fontify (Webschriften)

Verwaltet lokale Webschriften und liefert daraus fertiges `@font-face`-CSS sowie die eigentlichen Schriftdateien (woff, woff2). Version zum Zeitpunkt dieser Doku: 1.5.6. In der Bibliothek liegen aktuell 18 Schriften, darunter Barlow (die Standardschrift der Wetterwarte).

## Basis-URL

```
http://192.168.178.49:8765
```

## Fertiges CSS für eine Schrift

`GET /api/fonts/{font_name}/css`

Der wichtigste Endpunkt für die Einbindung: Er erzeugt die kompletten `@font-face`-Regeln für alle vorhandenen Schnitte einer Schrift.

Parameter:

- `font_name` (Pfad, Pflicht) - Name bzw. Ordner der Schrift, z. B. `Barlow`
- `base_url` (Query, optional) - Präfix, das den Schriftdateien im CSS vorangestellt wird

Antwort: `Content-Type: text/css`.

```bash
curl "http://192.168.178.49:8765/api/fonts/Barlow/css"
```

```css
/* Fontify - Barlow */
/* Weights: 100, 200, 300, 400 */

@font-face {
  font-family: 'Barlow';
  font-style: normal;
  font-weight: 100;
  font-display: swap;
  src: url("/fonts/Barlow/web/barlow-latin-100-normal.woff") format("woff"),
       url("/fonts/Barlow/web/barlow-latin-100-normal.woff2") format("woff2"),
       url("/fonts/Barlow/web/barlow-latin-ext-100-normal.woff") format("woff"),
       ...
}
```

### Wichtiger Hinweis zu `base_url`

Ohne `base_url` enthält das CSS relative Pfade der Form `/fonts/{Ordner}/web/...`. Diese funktionieren direkt, solange das CSS im selben Ursprung wie der Fontify-Dienst geladen wird.

Wird `base_url` gesetzt, ersetzt der Wert das Präfix vollständig. Der Dienst hängt dahinter direkt `/{Ordner}/web/...` an - also ohne das Segment `/fonts`. Damit die Adressen gültig bleiben, muss `base_url` das `/fonts` selbst enthalten:

- Richtig: `base_url=http://192.168.178.49:8765/fonts` ergibt `http://192.168.178.49:8765/fonts/Barlow/web/...` (funktioniert)
- Falsch: `base_url=http://192.168.178.49:8765` ergibt `http://192.168.178.49:8765/Barlow/web/...` (liefert `404`, weil das `/fonts`-Segment fehlt)

```bash
curl "http://192.168.178.49:8765/api/fonts/Barlow/css?base_url=http://192.168.178.49:8765/fonts"
```

## Schriftdateien direkt laden

Die einzelnen Dateien liegen statisch unter:

```
GET /fonts/{Ordner}/web/{Dateiname}
```

Beispiel:

```bash
curl -o barlow-400.woff2 "http://192.168.178.49:8765/fonts/Barlow/web/barlow-latin-400-normal.woff2"
```

Die Dateinamen folgen dem Muster `{schrift}-{subset}-{gewicht}-{stil}.{format}`, z. B. `barlow-latin-400-normal.woff2` (Subset `latin`, Gewicht 400, Stil normal). Verfügbare Subsets bei Barlow sind unter anderem `latin`, `latin-ext` und `vietnamese`. Diese Pfade müssen nicht selbst zusammengesetzt werden - das CSS aus dem vorigen Endpunkt referenziert sie bereits korrekt, und die Detailabfrage (siehe unten) listet jede Datei mit fertigem `path` auf.

## Schriften auflisten und Details abrufen

### Liste (paginiert)

`GET /api/fonts`

Parameter (alle optional): `page`, `per_page` (Minimum 5), `sort`, `order`, `filter`, `letter` (Anfangsbuchstabe), `search`.

```bash
curl "http://192.168.178.49:8765/api/fonts?page=1&per_page=20&sort=name&order=asc"
```

```json
{
  "fonts": [
    {
      "name": "Barlow",
      "folder": "Barlow",
      "weights": [100, 200, 300, 400],
      "formats": ["woff", "woff2"],
      "source": "Bunny Fonts",
      "web": { "count": 20, "size_human": "..." }
    }
  ],
  "pagination": { "page": 1, "per_page": 20, "total": 18, "total_pages": 1, "has_prev": false, "has_next": false },
  "stats": { "total_fonts": 18, "web": { "files": 300, "size_human": "10.0 MB" } }
}
```

Wichtige Antwortfelder: `fonts` (Liste), `pagination` (mit `total`, `total_pages`, `has_next`), `stats` (Kennzahlen der Bibliothek). Je Schrift: `name`, `folder`, `weights` (verfügbare Gewichte), `formats`, `source` (Herkunft), `web`/`desktop` (Dateizusammenfassung).

Alle Schriften ohne Blättern liefert `GET /api/fonts/all`.

### Details einer Schrift

`GET /api/fonts/{font_name}` - liefert die vollständige Beschreibung inklusive jeder einzelnen Datei mit fertigem Pfad.

```bash
curl "http://192.168.178.49:8765/api/fonts/Barlow"
```

```json
{
  "name": "Barlow",
  "folder": "Barlow",
  "weights": [100, 200, 300, 400],
  "formats": ["woff", "woff2"],
  "web": {
    "count": 20,
    "files": [
      {
        "name": "barlow-latin-400-normal.woff2",
        "format": "woff2",
        "weight": 400,
        "style": "normal",
        "size_human": "21.7 KB",
        "path": "/fonts/Barlow/web/barlow-latin-400-normal.woff2"
      }
    ]
  }
}
```

Jede Datei in `web.files` trägt die Felder `name`, `format`, `weight`, `style`, `size`/`size_human` und `path` (direkt ladbar, siehe oben).

## Schriften suchen

- `GET /api/fonts/search/local?q=...` - durchsucht die bereits vorhandene Bibliothek. Antwort: `{ "query", "results", ... }`, wobei jeder Treffer wie ein Detail-Objekt aufgebaut ist.
- `GET /api/fonts/search/online?q=...&limit=...` - schlägt herunterladbare Schriften aus Online-Quellen vor (`q` Pflicht, `limit` optional). Antwort: `{ "query", "results": [ { "family", "category", "variants" } ], "count" }`.

```bash
curl "http://192.168.178.49:8765/api/fonts/search/online?q=roboto&limit=2"
```

```json
{ "query": "roboto", "results": [ { "family": "Roboto", "category": "Sans Serif", "variants": 18 } ], "count": 2 }
```

## Weitere Endpunkte (Kurzreferenz)

Für das reine Einbinden vorhandener Schriften nicht nötig, aber zur Vollständigkeit:

| Methode und Pfad | Zweck |
|---|---|
| `GET /health` | Statusabfrage |
| `GET /api/fonts/stats` | Kennzahlen der Bibliothek (Anzahl, Größe, Quellen) |
| `GET /api/fonts/config/settings` | App-Einstellungen (z. B. `items_per_page`) |
| `POST /api/fonts/download` | Eine Schrift aus einer Online-Quelle herunterladen |
| `POST /api/fonts/download/github` | Schrift aus einem GitHub-Repository laden |
| `POST /api/fonts/upload` | Eigene Schriftdateien hochladen |
| `DELETE /api/fonts/{font_name}` | Schrift entfernen |
| `GET /api/fonts/{font_name}/package/web` | Web-Dateien einer Schrift als ZIP |
| `GET /api/fonts/{font_name}/package/desktop` | Desktop-Dateien (z. B. ttf/otf) als ZIP |
| `GET /api/fonts/{font_name}/package/full` | Komplettpaket einer Schrift als ZIP |
| `GET /api/fonts/package/all-web` | Alle Web-Schriften gebündelt |
| `GET /api/fonts/config/cdn`, `PUT`, `POST .../reset`, `POST /api/fonts/test-cdn` | Online-Quellen verwalten und testen |

## Grenzen, Aktualisierung und Frische (Fontify)

- Die Schriftdateien und das erzeugte CSS sind statisch und ändern sich nur, wenn eine Schrift hinzugefügt, aktualisiert oder gelöscht wird. Beides lässt sich damit dauerhaft zwischenspeichern.
- `per_page` bei `/api/fonts` akzeptiert keine Werte unter 5.
- Nicht jede Schrift liegt in jedem Gewicht vor. Barlow ist derzeit nur in den Gewichten 100 bis 400 vorhanden - für fette Schnitte (600/700) müsste die Schrift zuvor um diese Gewichte ergänzt werden. Vor dem Setzen fester Gewichte im CSS die tatsächlich verfügbaren `weights` über die Detailabfrage prüfen.
- Bei manchen Dateien meldet der Server als `Content-Type` `text/plain` statt eines Schrift-MIME-Typs. Für den Browser ist das unkritisch, da `@font-face` das Format über die `format(...)`-Angabe im CSS erkennt.

---

# Hinweise zur Nutzung in der Wetterwarte

- Icons und Schriften immer vom eigenen Pi laden, nie von einem fremden CDN. Beide Dienste sind genau dafür da und halten die Wetterwarte unabhängig und offline lauffähig.
- Schrift Barlow einbinden: entweder das fertige CSS von `GET /api/fonts/Barlow/css` einbetten oder - für maximale Unabhängigkeit - die benötigten `woff2`-Dateien einmalig herunterladen und lokal im Projekt ausliefern, mit einem eigenen `@font-face`-Block. Wird das CSS aus einem anderen Ursprung geladen, `base_url=http://192.168.178.49:8765/fonts` mitgeben (das `/fonts`-Segment nicht vergessen).
- Nur die tatsächlich genutzten Schnitte laden. Barlow bietet aktuell 100 bis 400; für die Kacheln reichen in der Regel 400 (normal) und, sofern vorhanden, ein kräftigeres Gewicht für Überschriften.
- Icons per API-Endpunkt `GET /api/icons/{set_id}/{icon_name}/svg?style=...` holen, weil er den Stil zuverlässig auflöst. Wenn ein Icon inline eingefärbt werden soll, das SVG einbetten und die Farbe per CSS (`color`/`fill`) an das Kachel-Design binden.
- Für Wetter-Symbole (Sonne, Wolke, Regen, Wind usw.) zuerst über `GET /api/icons/search?scope=all` nach dem passenden Namen suchen und dabei ein Set mit einheitlichem Stil wählen (z. B. durchgängig `material-symbols` im Stil `rounded`), damit alle Kacheln optisch zusammenpassen.
- Set-Lizenz beachten: bevorzugt Sets mit `license_category: permissive` verwenden; Font Awesome nur, wenn eine Namensnennung möglich ist.
- Beide Dienste als Voraussetzung behandeln: Vor dem Abruf per `GET /health` die Erreichbarkeit prüfen und Icons wie Schriften im Build oder Cache der Wetterwarte ablegen, damit die App auch bei kurzem Ausfall eines Dienstes weiter funktioniert.
