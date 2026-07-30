# Aufraeum-Log (spaeter, gesammelt)

Damit wir Dinge nicht mehrfach anfassen: hier wird notiert, was beim naechsten
bewussten Aufraeum-Durchgang erledigt wird. Nichts davon ist ein Fehler - es ist
nur noch nicht dran.

## Tote CSS-Klassen in `frontend/src/app.css`

Automatisch ermittelte Kandidaten (in keiner `.svelte`-Datei als Wort gefunden).
ACHTUNG: die Liste enthaelt FALSCH-POSITIVE - Klassen, die DYNAMISCH gesetzt
werden, tauchen im Quelltext nie woertlich auf. Vor dem Loeschen pruefen.

**Unbedingt behalten (werden dynamisch gesetzt):**
`t-frost` `t-kuehl` `t-warm` `t-extrem` (Temperaturfarben via `{tempKlasse}`),
`warnstufe-1..4` (via `warnstufe-{stufe}`), `hat-tipp` `tipp-blase` `sichtbar`
(Tooltip-Aktion `lib/tipp.ts`), evtl. `faellt` `steigt` `winzig` `nowrap` `mini`
`grad` `hz` `nr` `sk` `kw-fehler` (erst pruefen - teils fuer geplante Zustaende).

**Vermutlich wirklich tot (Mockup-Reste, nach Sichtpruefung entfernbar):**
`akz` `ansicht-umschalter` `avatar` `brett` `detail` `dunkelkarte` `galerie`
`galerie-kopf` `galerie-seite` `galerie-titel` `galerie-unter` `zur-galerie`
`h5` `handy` `handy-buehne` `heatmap` `kachel-platz` `karte-link` `mini-ort`
`mit-detail` `mock-leiste` `nav-aus` `nutzer-chip` `schliessen` `schmal`
`sonnenuntergang` `trenn` `w2`..`w12` `waehlbar` `warn-punkt`

Erledigt bereits: `.tchart`, `.chart-flaeche`.

## Kleinkram Backend

- `schemas/envelope.py`: getypte Modelle werden nirgends als `response_model`
  genutzt (alle bauen den Umschlag per `wrap()`) - einsetzen oder loeschen.
- `routers/archiv.py`: `verlauf(ort="koeln")` - Default nicht mehr auf einen
  festen Ort setzen (aus dem Start-Ort ableiten oder Pflichtparameter).
- `orte.py` Docstring vs. Seed: der Seed legt Demo-Orte an - Docstring dazu
  praezisieren.
