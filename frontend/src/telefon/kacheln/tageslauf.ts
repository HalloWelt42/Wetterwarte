// Tageslauf am Ort für die Kacheln Heute, Regen, Sonne und UV: die Stunden von heute und das nächste
// Sonnenereignis. Kalendertage in der Zeitzone des Orts (kern/zeit.ts); Zeitpunkte werden über die
// absolute Zeit verglichen.
import { kalendertag } from "../../kern/zeit";
import type { Kompakt, Stunde } from "../typen";

/** Stunden der Liste, die auf den ersten Vorhersagetag (heute) fallen, mit ihrer Lage in der Liste. */
export function stundenHeute(d: Kompakt, zone: string): { s: Stunde; i: number }[] {
  const heute = d.tage[0]?.datum;
  return d.stunden.map((s, i) => ({ s, i })).filter(({ s }) => kalendertag(s.zeit, zone) === heute);
}

/** Anzahl der kommenden Stunden (ab der laufenden), die noch zu heute gehören. */
export function restStundenHeute(d: Kompakt, zone: string): number {
  return stundenHeute(d, zone).filter(({ i }) => i >= d.jetzt_index).length;
}

export interface Sonnenereignis {
  art: "auf" | "unter";
  zeit: string;
}

/** Nächstes Sonnenereignis nach jetzt: Aufgang heute, Untergang heute oder Aufgang morgen. */
export function naechstesSonnenereignis(d: Kompakt, jetzt: Date): Sonnenereignis | null {
  const [heute, morgen] = d.tage;
  const t = jetzt.getTime();
  if (heute?.sonnenaufgang && t < Date.parse(heute.sonnenaufgang)) return { art: "auf", zeit: heute.sonnenaufgang };
  if (heute?.sonnenuntergang && t < Date.parse(heute.sonnenuntergang)) return { art: "unter", zeit: heute.sonnenuntergang };
  if (morgen?.sonnenaufgang) return { art: "auf", zeit: morgen.sonnenaufgang };
  return null;
}

/** Sekunden von jetzt bis zu einem Zeitpunkt (nie negativ). */
export function sekundenBis(zeit: string, jetzt: Date): number {
  return Math.max(0, (Date.parse(zeit) - jetzt.getTime()) / 1000);
}
