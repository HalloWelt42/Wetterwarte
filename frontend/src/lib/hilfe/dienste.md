---
title: System & Dienste
subtitle: Welche Dienste laufen
category: Hintergrund
icon: fa-diagram-project
---

# System & Dienste

Ueber das Zahnrad oben oeffnest du die Dienste-Uebersicht. Sie zeigt alle Dienste,
die die Wetterwarte nutzt, mit Live-Status und Latenz - damit die Zusammenhaenge
klar sind und nichts im Verborgenen haengt.

## Gruppen

- **Intern** - App-Backend, PostgreSQL, Redis. Laufen im selben Verbund.
- **Lokal auf dem Pi** - eigene Dienste ohne externen Abruf zur Laufzeit:
  der Kartendienst (Deutschland als eigener Vektor-Render) und der Welt-Kachel-
  und Blitz-Dienst.
- **Externe Rohdaten** - die einzige Aussenanbindung: die Wetter-Rohdaten
  (Vorhersage, amtliche Warnungen, Pollen).

Ein gruener Punkt heisst erreichbar, gelb gestoert, rot nicht erreichbar. Mit dem
Knopf oben rechts pruefst du erneut.
