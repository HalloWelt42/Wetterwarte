// Kleine Auswertungen der Telefon-Antwort, die mehrere Kacheln und Blätter brauchen.
import { stunde as stundeIn } from "../kern/zeit";
import type { Kompakt, Stunde } from "./typen";

/** Stunden ab jetzt (die laufende zuerst). */
export function kommende(d: Kompakt, anzahl: number): Stunde[] {
  return d.stunden.slice(d.jetzt_index, d.jetzt_index + anzahl);
}

/** Erste kommende Stunde mit nennenswertem Regen (Wahrscheinlichkeit ab 50 % oder ab 0,2 mm). */
export function regenAb(d: Kompakt, stunden = 24): Stunde | null {
  return kommende(d, stunden).find((s) => (s.regen_wahrsch ?? 0) >= 50 || s.regen_mm >= 0.2) ?? null;
}

/** Kurzer Kopfzusatz "Regen ab 17 Uhr" (oder leer, wenn es trocken bleibt). */
export function regenAbText(d: Kompakt, mitUhr = true): string {
  const s = regenAb(d);
  if (!s) return "";
  if (s === d.stunden[d.jetzt_index]) return "Regen jetzt";
  return `Regen ab ${stundeIn(s.zeit, d.ort.zeitzone)}${mitUhr ? " Uhr" : ""}`;
}

/** Hoch und Tief von heute (erster Vorhersagetag). */
export function heute(d: Kompakt): { hoch: number; tief: number } | null {
  const t = d.tage[0];
  return t ? { hoch: t.hoch, tief: t.tief } : null;
}

/** Warnlage am Ort: Liste (auch leer), Quelle ausgefallen, oder Ort außerhalb des Warngebiets
 *  (der Wetterdienst warnt nur für Deutschland; dann gibt es schlicht keine amtlichen Warnungen). */
export type Warnlage = "liste" | "unbekannt" | "ausserhalb";

export function warnlage(d: Kompakt): Warnlage {
  if (d.bereiche.warnungen.status === "fehlt") return "unbekannt";
  return d.warnungen === null ? "ausserhalb" : "liste";
}
