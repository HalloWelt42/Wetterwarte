---
title: System & Dienste
subtitle: Welche Dienste laufen
category: Hintergrund
icon: fa-diagram-project
---

# System & Dienste

Über das Zahnrad oben öffnest du die Dienste-Übersicht. Sie zeigt alle Dienste,
die die Wetterwarte nutzt, mit Live-Status und Latenz - damit die Zusammenhänge
klar sind und nichts im Verborgenen hängt.

## Gruppen

- **Intern** - App-Backend, PostgreSQL, Redis. Laufen im selben Verbund.
- **Lokal auf dem Pi** - eigene Dienste ohne externen Abruf zur Laufzeit:
  der Kartendienst (Deutschland als eigener Vektor-Render) und der Welt-Kachel-
  und Blitz-Dienst.
- **Externe Rohdaten** - die einzige Außenanbindung: die Wetter-Rohdaten
  (Vorhersage, amtliche Warnungen, Pollen).

Ein grüner Punkt heißt erreichbar, gelb gestört, rot nicht erreichbar. Mit dem
Knopf oben rechts prüfst du erneut.
