# Offene Wuensche (laufender Backlog)

Gesammelte Wuensche aus der Weiterentwicklung, in grober Reihenfolge. Erledigtes
wird abgehakt; die App-Version im Fuss zeigt den Live-Stand.

## Erledigt (Auszug seit v0.18)
- [x] Dienste-Uebersicht unter Einstellungen (Zahnrad), Live-Status intern/lokal/extern (v0.18)
- [x] Freischwebende Hilfe mit Volltextsuche + Mini-i-Deeplinks (v0.19)
- [x] Echte Inline-Ortssuche im Kopf (v0.20)
- [x] Aufzeichnungs-Manager funktional; Dunkelmodus+Atmosphaere stimmig (v0.21)
- [x] Karten-Einstellungen als gemeinsamer Store; Mini-Karte folgt der grossen Karte (v0.22)
- [x] Uhr- und Kalender-Kacheln, mehrere Varianten (v0.23)
- [x] Kachel-Resize-Winkelsymbol weg, blau gestrichelter Ablage-Platzhalter; Uhr-Zeitzone (IANA); Mini-Karten-Pin (v0.24)
- [x] Luftschadstoffe aufzeichenbar; Datenfrische-Ring im Kopf (v0.25)
- [x] Orte per Drag-and-Drop umsortieren (Sidebar), Reihenfolge persistent (v0.26)
- [x] Klima-Diagramm-Widget (Monatsnormale, gespeichert) (v0.27)
- [x] Zeitzonen pro Ort in Sonne/Mond/Uhr korrekt; ruhiger Glow um die Tagsonne (v0.29)
- [x] Klimadaten als Monatsaggregate in der DB; Jahresmesswerte-Diagramm (Jahres-Blaetterung, aktueller Monat markiert, Hover-Bubble) (v0.30)

- [x] Hover-Tooltips in allen Diagrammen (LinienChart/Klima/Nowcast/Jahresmesswerte) + aktueller Monat/jetzt markiert; adversarial geprueft + Fixes (v0.31.0)
- [x] Zeitzonen vollstaendig: Wetterdaten in lokaler Ortszeit (timezone=auto), Bestandsorte nachgezogen - New York stimmt (v0.31.1)
- [x] Hilfe deutlich ausgebaut: 14 Themen in 4 Bereichen (Dropdown gegliedert), Tiefenlinks je Kacheltyp + in Aufzeichnung/Archiv/Dienste; adversarial geprueft (v0.32.0)
- [x] Katalog zeigt je Kachel, wie oft sie im aktuellen Profil gesetzt ist (v0.32.0)
- [x] Grosskarte: eigenes DWD-RADOLAN-Regenradar (RY gemessen + RV-Nowcast bis +2h), reprojiziertes Bild-Overlay mit Abspiel-Zeitleiste + mm/h-Legende (v0.33.0)
- [x] Radardaten optional historisch speichern (DB-Archiv, Schalter+Aufbewahrung), Abspieler blaettert weiter zurueck (v0.34.0)
- [x] Mini-Karte: aktueller Radar-Stand (ohne Abspieler) + Icon-Schalter (Beschriftung/Blitze/Radar); Radar-Steuerung der grossen Karte repariert (v0.35.0)
- [x] Warnungen-Overlay: amtliche DWD-Warn-Polygone farbig nach Stufe, Klick-Popup, Zaehler (v0.36.0)

## Offen
- [ ] Grosskarte-Rest: Overlays Temperatur + Wind funktional (Open-Meteo-Gitter); vereinfachte Vektor-Karte (osmlocal-Vektor)
- [ ] Offline-Cache themengetrennt; Speicher-Statistik sichtbar; Prozessbalken bei Daten-Aggregation in den Einstellungen mit vollstaendiger Fehler-/Fertig-Logik; Fuell-Bot (naeher am Wohnort mehr, Satellit progressiv)
- [ ] Demo-Profile zum Ausprobieren: Orte mit Extremwetter + bekannte Orte
- [ ] Rettungsring / Onboarding fuer Erstnutzer (Muster wie im Projekt RadioHub)
- [ ] Spendenlogik (Muster wie RadioHub / Smart-Translator-Spende-Block)
- [ ] README mit Screenshot (Screenshot OHNE den Ort "Zeitz")
- [ ] Lizenzen aller Abhaengigkeiten pruefen, LICENSE entsprechend anpassen (Referenz RadioHub)
- [ ] Mobile-Ansicht optimieren - ganz zum Schluss, wenn alles andere fertig ist

Referenzen: RadioHub (github.com/HalloWelt42/RadioHub) fuer Spenden + Lizenzen;
hilfe-fenster-demo (bereits uebernommen).
