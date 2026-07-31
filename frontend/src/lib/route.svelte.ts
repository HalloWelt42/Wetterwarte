// Reaktives Routing zwischen den Hauptansichten - mit echten Deep-Links ueber
// die History-API (ohne Hash), damit Neuladen, Teilen und Zurueck/Vorwaerts die
// Ansicht und den aktiven Ort erhalten.
//
// Ansicht und Ort stehen als Query-Parameter am Wurzelpfad, z. B.
// /?ansicht=karte&ort=hamburg. Bewusst KEINE Pfad-Segmente: /api, /karte und
// /kachel sind bereits Proxy-Pfade (Backend bzw. Kartenserver) - ein Client-Pfad
// /karte wuerde damit kollidieren. Der Wurzelpfad wird immer als App ausgeliefert.
export type Ansicht = "dashboard" | "karte" | "aufzeichnung" | "archiv";

const ANSICHTEN: Ansicht[] = ["dashboard", "karte", "aufzeichnung", "archiv"];

function ansichtAusUrl(): Ansicht {
  if (typeof location === "undefined") return "dashboard";
  const a = new URLSearchParams(location.search).get("ansicht") as Ansicht | null;
  return a && ANSICHTEN.includes(a) ? a : "dashboard";
}

export function ortAusUrl(): string {
  if (typeof location === "undefined") return "";
  return new URLSearchParams(location.search).get("ort") ?? "";
}

export const route = $state<{ ansicht: Ansicht }>({ ansicht: ansichtAusUrl() });

function baueUrl(ansicht: Ansicht, ort: string): string {
  const p = new URLSearchParams();
  if (ansicht !== "dashboard") p.set("ansicht", ansicht);
  if (ort) p.set("ort", ort);
  const qs = p.toString();
  return qs ? `${location.pathname}?${qs}` : location.pathname;
}

// Ansicht wechseln -> neuer History-Eintrag (Zurueck-Taste blaettert Ansichten).
export function gehe(ansicht: Ansicht): void {
  if (route.ansicht === ansicht) return;
  route.ansicht = ansicht;
  if (typeof history !== "undefined") history.pushState({ ansicht }, "", baueUrl(ansicht, ortAusUrl()));
}

// Aktiven Ort in der URL spiegeln, ohne die Ansicht zu wechseln. Ersetzt den
// aktuellen Eintrag (kein History-Spam bei jedem Ortswechsel).
export function setzeOrtInUrl(ort: string): void {
  if (typeof history === "undefined") return;
  if (ortAusUrl() === ort) return;
  history.replaceState({ ansicht: route.ansicht }, "", baueUrl(route.ansicht, ort));
}

// Beim ersten Aufruf die URL auf den Startzustand normalisieren (z. B. Ort ergaenzen).
export function initUrl(ort: string): void {
  if (typeof history === "undefined") return;
  history.replaceState({ ansicht: route.ansicht }, "", baueUrl(route.ansicht, ort));
}

// Zurueck/Vorwaerts im Browser folgt der Ansicht aus der URL.
if (typeof window !== "undefined") {
  window.addEventListener("popstate", () => {
    route.ansicht = ansichtAusUrl();
  });
}
