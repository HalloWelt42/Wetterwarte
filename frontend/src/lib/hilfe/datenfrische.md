---
title: Datenfrische
subtitle: Wie oft welche Daten kommen
category: Hintergrund
icon: fa-arrows-rotate
---

# Datenfrische

Nicht alles ist gleich zeitkritisch. Darum frischt jede Datenart in ihrem eigenen
Takt auf - zeitkritisches oft, träges selten. Die Kacheln aktualisieren sich
dadurch von selbst.

| Bereich | Takt |
|---|---|
| Warnungen | ~2 Minuten |
| Blitze | ~1,5 Minuten (Karte: live) |
| Aktuell / Vorhersage / Nowcast | ~10 Minuten |
| Luftqualität | ~15 Minuten |
| Pollen | ~1 Stunde |

Kehrst du zum Tab zurück, werden die zeitkritischen Bereiche sofort aufgefrischt.

Im Hintergrund teilt sich alles, was denselben Ort und Bereich braucht, **eine**
Abfrage (Zwischenspeicher), damit nicht unnötig oft geladen wird.
