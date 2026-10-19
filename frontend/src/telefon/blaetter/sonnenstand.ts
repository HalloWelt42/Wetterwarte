// Zusatzzeiten im Sonnenblatt (Höchststand, goldene Stunde, Ende der Dämmerung), gerechnet aus der
// Sonnendeklination des Tages und verankert an Auf- und Untergang aus den Daten. Dadurch auf wenige
// Minuten genau; wo die Sonne die nötige Höhe nicht erreicht (hoher Norden), gibt es keinen Wert.

const RAD = Math.PI / 180;

/** Deklination der Sonne in Grad für einen Kalendertag ("2026-10-19"), Näherung nach NOAA. */
function deklination(datum: string): number {
  const [j, m, t] = datum.split("-").map(Number);
  const tagImJahr = (Date.UTC(j, m - 1, t) - Date.UTC(j, 0, 1)) / 86_400_000;
  const g = ((2 * Math.PI) / 365) * tagImJahr;
  const d =
    0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) -
    0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
  return d / RAD;
}

/** Stundenwinkel in Grad, bei dem die Sonne die Höhe h erreicht; null, wenn sie das nicht tut. */
function stundenwinkel(breite: number, dekl: number, h: number): number | null {
  const c = (Math.sin(h * RAD) - Math.sin(breite * RAD) * Math.sin(dekl * RAD)) / (Math.cos(breite * RAD) * Math.cos(dekl * RAD));
  return c < -1 || c > 1 ? null : Math.acos(c) / RAD;
}

export interface Zusatzzeiten {
  mittag: Date; // Höchststand: Mitte zwischen Auf- und Untergang
  hoehe: number; // Höhe der Sonne am Mittag in Grad
  goldeneStunde: Date | null; // Sonne sinkt unter 6 Grad
  daemmerungEnde: Date | null; // Sonne 6 Grad unter dem Horizont (bürgerliche Dämmerung)
}

export function zusatzzeiten(datum: string, breite: number, aufgang: string, untergang: string): Zusatzzeiten {
  const auf = new Date(aufgang).getTime();
  const unter = new Date(untergang).getTime();
  const dekl = deklination(datum);
  const h0 = stundenwinkel(breite, dekl, -0.833); // Auf- und Untergang mit Brechung
  const h6 = stundenwinkel(breite, dekl, 6);
  const hd = stundenwinkel(breite, dekl, -6);
  const ms = (grad: number) => (grad / 15) * 3_600_000;
  return {
    mittag: new Date((auf + unter) / 2),
    hoehe: 90 - Math.abs(breite - dekl),
    goldeneStunde: h0 !== null && h6 !== null ? new Date(unter - ms(h0 - h6)) : null,
    daemmerungEnde: h0 !== null && hd !== null ? new Date(unter + ms(hd - h0)) : null,
  };
}
