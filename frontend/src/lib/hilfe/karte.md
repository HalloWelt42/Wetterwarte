---
title: Karte
subtitle: Basiskarten, Orientierung, Blitze
category: Ansichten
icon: fa-map-location-dot
---

# Karte

Die große Karte erreichst du links über **Große Karte**. Im Panel links
steuerst du Darstellung und Ebenen.

## Basiskarte

- **Hell** und **Dunkel** - schlichte Karten.
- **Satellit** - Luftbild.

Die Basiskarten kommen über unseren eigenen Kartendienst auf dem Pi (Deutschland
als eigener Vektor-Render) bzw. den lokalen Welt-Kachel-Dienst.

## Beschriftung & Grenzen

Ein Schalter blendet **Ortsnamen, Grenzen und Straßen** zusätzlich ein - vor
allem für die Satellitenkarte und die datenarme Dunkelkarte zur Orientierung.

## Overlays

Ebenen wie **Blitze** liegen über der Karte. Die Blitze kommen live.

## Temperatur & Wind

Das **Temperatur**-Overlay legt ein glattes Farbfeld (Legende in °C) über
Deutschland - genau auf die Landesgrenze zugeschnitten. Fährst du mit der Maus
darüber, zeigt eine Sprechblase die Temperatur an der Position. Das **Wind**-
Overlay zeigt Richtungspfeile im Gitter; Farbe und Größe stehen für die Stärke,
ein Klick nennt Tempo und Richtung.

## Regen-Radar

Das Radar zeigt den echten Niederschlag aus dem eigenen DWD-RADOLAN-Bezug - farbig
nach Regenrate (mm/h, siehe Legende). Unten läuft ein **Abspieler**: die gemessene
Vergangenheit der letzten Minuten und anschließend die **Vorhersage bis +2 Stunden**
(orange gekennzeichnet). Mit dem Schieber springst du zu einem Zeitpunkt, mit dem
Knopf hältst du an oder spielst weiter. Die Rohdaten liegen bei uns lokal vor und
werden selbst gerendert.

## Blitz-Wellen (Simulation)

Optional zeigt die Karte je Blitz ein kurzes **Aufblitzen am Punkt** und eine
abklingende **Schallwelle** (Ring) - live über eine WebSocket-Verbindung. Der
Ort deiner Heimat ist mit einer **Pinnnadel** markiert.
