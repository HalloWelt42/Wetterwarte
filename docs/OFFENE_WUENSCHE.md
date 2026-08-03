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

- [x] Overlays Temperatur (Farbfeld, auf Deutschland zugeschnitten, Maus-Hover + Legende) + Wind (Richtungspfeile, auf DE zugeschnitten, Klick-Popup); Blitz-Menge einstellbar; Warn-Popup dunkelmodusfest + zeigt alle Ueberlappungen (v0.37-0.38.1)

- [x] Offline-Kartencache (Server): Kacheln themengetrennt auf Platte (Bind-Mount), Fuell-Bot (Deutschland + Wohnort-gewichtet) mit Fortschritt/Fehler/Fertig, Speicher-Statistik je Thema in den Einstellungen (v0.39.0)

- [x] Archiv/Analyse: Variablen-Auswahl dynamisch (alle aufgezeichneten Werte inkl. Luftqualitaet) (v0.39.2)
- [x] Demo-Orte zum Ausprobieren: Extremwetter + bekannte Orte, per Globus-Knopf hinzufuegbar (v0.40.0)

- [x] Rettungsring/Onboarding fuer Erstnutzer + "Danke sagen"-Overlay (Ko-fi zuoberst mit QR, Krypto BTC/DOGE/ETH mit QR + Kopieren, pulsierendes Spendenherz im Kopf) (v0.41.0)
- [x] README mit Screenshot (ohne den Ort "Zeitz") + Lizenzabschnitt; LICENSE (NC v1.0) angelegt (v0.41.0)
- [x] Regenradar: Umschalter Animation/Live (Live zeigt nur den aktuellen Stand) (v0.41.0)
- [x] Redundanten Karten-Overlay "Niederschlag-Nowcast" entfernt (steckt bereits im Radar-Overlay) (v0.41.0)
- [x] Deep-Links ohne Hash: Ansicht + Ort in der URL (History-API), neuladefest und teilbar (v0.41.0)
- [x] Dark-Mode-Schriftkontrast angehoben; Overlay-Stapelordnung (z-index) vereinheitlicht, Hilfe-Fenster tritt beim Oeffnen eines Modals zurueck (v0.41.0)
- [x] Aufzeichnungs-Takt einstellbar (5-60 min, Standard 10) im Aufzeichnungs-Manager; loest den fest verdrahteten 10-min-Takt ab (v0.42.0)
- [x] Mobile-Ansicht: Navigations-Schublade (Hamburger) mit Orte/Ansichten/Layouts/Mehr - vorher war die Sidebar auf Mobil unerreichbar; Kopfleiste entzerrt, Karten-Steuerung entzerrt (v0.43.0)
- [x] Profil-/Widget-Unabhaengigkeit: alle Tile-IDs global eindeutig (UUID) statt kollidierender typ-i/typ-x-y (Backend-Migration bestehender Layouts); Karten-Kacheln pro Instanz statt globalem karteEinst (Overlays/Basis in der conf je Kachel); Uebersicht-Eintrag in ANSICHTEN (sauberer Rueckweg aus Karte/Aufzeichnung/Archiv); Deep-Link ?profil=<id> (Profil neuladefest + teilbar) (v0.44.0)
- [x] Profil-Icon aus kuratiertem Pool waehlbar (Layout-Verwaltung, Kopf-Tabs + Nav rendern es); Minikarte mit mehr Options-Buttons (Basiskarte, Warnungen, Temperatur zusaetzlich); Karten-Crash beim Ansichtswechsel behoben (Zugriff auf entfernte Karte in laufenden Callbacks); Katalog-Titel im Dunkelmodus lesbar (Button erbte schwarze Standardfarbe) (v0.45.0)

## Offen
- [ ] Vereinfachte Vektor-Karte als Basiskarte (osmlocal-Vektorstil colorful/eclipse) - optional/kosmetisch.
  Bewusst zurueckgestellt: der Stil deckt nur Deutschland ab und braucht map.setStyle(), was alle
  programmatisch gebauten Overlays (Radar/Warnungen/Temperatur/Wind/Blitze/Beschriftung) verwirft und
  einen kompletten Neuaufbau danach erfordert - Regressionsrisiko fuer rein kosmetischen, DE-only-Gewinn.

Referenzen: RadioHub (github.com/HalloWelt42/RadioHub) fuer Spenden + Lizenzen;
hilfe-fenster-demo (bereits uebernommen).
