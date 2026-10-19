// Einstellungen dieses Geräts (nicht im Profil): Schriftstufe und Nachtbetrieb. Liegen im
// Gerätespeicher, weil jedes Telefon andere Augen und andere Nächte hat.
import { lies, schreib } from "../kern/speicher";

export type Stufe = "normal" | "gross" | "sehr-gross";
export type Nachtwahl = "aus" | "auto" | "an";

export const geraet = $state<{ stufe: Stufe; nacht: Nachtwahl }>({
  stufe: lies<Stufe>("telefon.stufe", "normal"),
  nacht: lies<Nachtwahl>("telefon.nacht", "auto"), // Standard: nach Sonnenauf- und -untergang am gewählten Ort
});

export function setzeStufe(stufe: Stufe): void {
  geraet.stufe = stufe;
  schreib("telefon.stufe", stufe);
}

export function setzeNacht(nacht: Nachtwahl): void {
  geraet.nacht = nacht;
  schreib("telefon.nacht", nacht);
}

/** Zur Desktop-Ansicht wechseln und die Wahl für dieses Gerät merken (index.html liest sie). */
export function zurDesktopAnsicht(): void {
  schreib("ansicht", "desktop");
  location.href = "/" + location.search;
}
