// Was die Karte im Telefon zeigt: jede Ebene schaltet einzeln und unabhängig, die Wahl merkt sich
// das Gerät (Schlüssel "telefon.karte"). Unabhängig von den Karteneinstellungen am Rechner.
import { lies, schreib } from "../../../kern/speicher";

export interface KartenWahl {
  blitze: boolean;
  warnungen: boolean;
  dunkel: boolean; // Grundkarte dunkel, sonst hell
  detail: boolean; // Beschriftung und Straßen als zusätzliche Ebene
  radar: boolean;
  wind: boolean;
}

export type Ebene = keyof KartenWahl;

const STANDARD: KartenWahl = { blitze: true, warnungen: true, dunkel: true, detail: false, radar: true, wind: false };

/** Schalter am rechten Rand, von oben nach unten. */
export const SCHALTER: { ebene: Ebene; symbol: string; titel: string }[] = [
  { ebene: "blitze", symbol: "fa-bolt", titel: "Gewitter und Blitze" },
  { ebene: "warnungen", symbol: "fa-triangle-exclamation", titel: "Warnungen" },
  { ebene: "dunkel", symbol: "fa-circle-half-stroke", titel: "Dunkle Grundkarte" },
  { ebene: "detail", symbol: "fa-map", titel: "Detailkarte" },
  { ebene: "radar", symbol: "fa-cloud-rain", titel: "Regenradar" },
  { ebene: "wind", symbol: "fa-wind", titel: "Wind" },
];

/** Gemerkte Wahl lesen; nur bekannte Ebenen mit Wahrheitswert zählen, sonst gilt der Standard. */
function gemerkt(): KartenWahl {
  const roh = lies<Record<string, unknown>>("telefon.karte", {});
  const wahl = { ...STANDARD };
  for (const e of Object.keys(STANDARD) as Ebene[]) if (typeof roh?.[e] === "boolean") wahl[e] = roh[e] as boolean;
  return wahl;
}

export const kartenWahl = $state<KartenWahl>(gemerkt());

export function schalte(ebene: Ebene): void {
  kartenWahl[ebene] = !kartenWahl[ebene];
  schreib("telefon.karte", $state.snapshot(kartenWahl));
}
