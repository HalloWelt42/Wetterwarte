// Gemeinsamer, reaktiver Karten-Einstellungs-Store: Basiskarte, Orientierungs-Ebene,
// Overlays und Simulation. Grosse Karte UND Mini-Karte lesen daraus, damit die
// Mini-Karte auf dem Dashboard denselben Einstellungen folgt wie die grosse Ansicht.
// Wird in localStorage gemerkt.
import { lies, schreib } from "./speicher";

const OVERLAYS_STANDARD: Record<string, boolean> = {
  blitze: true,
  warnungen: false,
  radar: false,
  wind: false,
  nowcast: false,
  temperatur: false,
};

export const karteEinst = $state<{
  basis: "hell" | "dunkel" | "satellit";
  orientierung: boolean;
  overlays: Record<string, boolean>;
  simulation: boolean;
}>({
  basis: lies("karte.basis", "hell"),
  orientierung: lies("karte.orientierung", false),
  overlays: { ...OVERLAYS_STANDARD, ...lies("karte.overlays", {}) },
  simulation: lies("karte.simulation", false),
});

// Aenderungen dauerhaft merken (App-weiter Wurzel-Effekt).
$effect.root(() => {
  $effect(() => schreib("karte.basis", karteEinst.basis));
  $effect(() => schreib("karte.orientierung", karteEinst.orientierung));
  $effect(() => schreib("karte.overlays", karteEinst.overlays));
  $effect(() => schreib("karte.simulation", karteEinst.simulation));
});

// Provider-Zuordnung der Basiskarten (fuer beide Karten gleich).
export const KARTEN_PROVIDER: Record<string, string> = { hell: "light", dunkel: "dark", satellit: "satellite" };
export const kachelUrl = (basis: string): string[] => [`/kachel/${KARTEN_PROVIDER[basis] ?? "light"}/{z}/{x}/{y}`];
