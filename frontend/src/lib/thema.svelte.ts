// Reaktiver Theme-Zustand (hell/dunkel) ueber [data-theme] am <html>-Element.
// Die Wahl wird gemerkt (localStorage) und beim Laden sofort angewandt, damit
// ein gemerktes "dunkel" nicht kurz hell aufblitzt.
import { lies, schreib } from "./speicher";

export const thema = $state<{ wert: "hell" | "dunkel" }>({ wert: lies("thema", "hell") });

// Gemerkte Wahl direkt beim Import anwenden (vor dem ersten Rendern).
if (typeof document !== "undefined") document.documentElement.dataset.theme = thema.wert;

export function setzeThema(wert: "hell" | "dunkel"): void {
  thema.wert = wert;
  document.documentElement.dataset.theme = wert;
  schreib("thema", wert);
}

export function themaUmschalten(): void {
  setzeThema(thema.wert === "hell" ? "dunkel" : "hell");
}
