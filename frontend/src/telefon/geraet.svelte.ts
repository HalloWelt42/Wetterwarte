// Einstellungen dieses Geräts (nicht im Profil): Schriftstufe und Nachtbetrieb. Liegen im
// Gerätespeicher, weil jedes Telefon andere Augen und andere Nächte hat.
import { lies, schreib } from "../kern/speicher";

export type Stufe = "normal" | "gross" | "sehr-gross";
export type Nachtwahl = "aus" | "auto" | "an";

/** Von Hand umgeschaltet, während die Zeitsteuerung läuft: gilt bis zum nächsten Sonnenauf- oder
 *  -untergang (Zeitpunkt in ms), danach übernimmt wieder die Automatik. */
export interface Uebersteuerung {
  nacht: boolean;
  bis: number;
}

export const geraet = $state<{ stufe: Stufe; nacht: Nachtwahl; uebersteuerung: Uebersteuerung | null }>({
  stufe: lies<Stufe>("telefon.stufe", "normal"),
  nacht: lies<Nachtwahl>("telefon.nacht", "auto"), // Standard: nach Sonnenauf- und -untergang am gewählten Ort
  uebersteuerung: lies<Uebersteuerung | null>("telefon.nacht.uebersteuerung", null),
});

export function setzeStufe(stufe: Stufe): void {
  geraet.stufe = stufe;
  schreib("telefon.stufe", stufe);
}

export function setzeNacht(nacht: Nachtwahl): void {
  geraet.nacht = nacht;
  schreib("telefon.nacht", nacht);
  setzeUebersteuerung(null);
}

export function setzeUebersteuerung(u: Uebersteuerung | null): void {
  geraet.uebersteuerung = u;
  schreib("telefon.nacht.uebersteuerung", u);
}
