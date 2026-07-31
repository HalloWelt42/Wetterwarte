---
title: Datenquellen
subtitle: Woher die Daten kommen
category: Hintergrund
icon: fa-cloud-arrow-down
---

# Datenquellen

Leitgedanke der Wetterwarte ist Unabhängigkeit: Außer den reinen Wetter-Rohdaten
läuft alles lokal auf dem eigenen Rechner bzw. dem Pi.

## Rohdaten (die einzige Außenanbindung)

- **Vorhersage, aktuelle Werte, Sonne, Luftqualität, Klima-Archiv** stammen aus
  einem offenen Wetterdienst. Die Zeiten kommen in der Zeitzone des jeweiligen
  Ortes.
- **Amtliche Warnungen** und **Pollenflug** kommen vom Deutschen Wetterdienst.

## Lokal auf dem Pi

- **Karten**: Deutschland wird als eigener Vektor-Render bereitgestellt, die
  weltweiten Kartenkacheln über einen lokalen Kachel-Dienst.
- **Blitze**: ein eigener Dienst liefert die Live-Blitze.
- **Archiv**: deine aufgezeichneten Messwerte liegen in einer lokalen Datenbank.

## Nennung der Quellen

Die Nennung von Deutschem Wetterdienst, dem offenen Wetterdienst und
OpenStreetMap erfolgt als vorgeschriebene Quellenangabe - sie ist rechtlich
geboten und keine Werbung. Die genaue Erreichbarkeit aller Bausteine siehst du
unter *System & Dienste*.
