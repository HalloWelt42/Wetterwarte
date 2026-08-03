// Reaktives Routing zwischen den Hauptansichten - mit echten Deep-Links ueber
// die History-API (ohne Hash), damit Neuladen, Teilen und Zurueck/Vorwaerts die
// Ansicht, den aktiven Ort und das aktive Profil erhalten.
//
// Ansicht, Ort und Profil stehen als Query-Parameter am Wurzelpfad, z. B.
// /?ansicht=karte&ort=hamburg&profil=<id>. Bewusst KEINE Pfad-Segmente: /api,
// /karte und /kachel sind bereits Proxy-Pfade - ein Client-Pfad /karte wuerde
// kollidieren. Der Wurzelpfad wird immer als App ausgeliefert.
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

export function profilAusUrl(): string {
  if (typeof location === "undefined") return "";
  return new URLSearchParams(location.search).get("profil") ?? "";
}

export const route = $state<{ ansicht: Ansicht }>({ ansicht: ansichtAusUrl() });

function baueUrl(ansicht: Ansicht, ort: string, profil: string): string {
  const p = new URLSearchParams();
  if (ansicht !== "dashboard") p.set("ansicht", ansicht);
  if (ort) p.set("ort", ort);
  if (profil) p.set("profil", profil);
  const qs = p.toString();
  return qs ? `${location.pathname}?${qs}` : location.pathname;
}

// Ansicht wechseln -> neuer History-Eintrag (Zurueck-Taste blaettert Ansichten).
export function gehe(ansicht: Ansicht): void {
  if (route.ansicht === ansicht) return;
  route.ansicht = ansicht;
  if (typeof history !== "undefined") history.pushState({ ansicht }, "", baueUrl(ansicht, ortAusUrl(), profilAusUrl()));
}

// Aktiven Ort in der URL spiegeln, ohne die Ansicht zu wechseln (ersetzt den Eintrag).
export function setzeOrtInUrl(ort: string): void {
  if (typeof history === "undefined" || ortAusUrl() === ort) return;
  history.replaceState({ ansicht: route.ansicht }, "", baueUrl(route.ansicht, ort, profilAusUrl()));
}

// Aktives Profil (Layout-ID) in der URL spiegeln (ersetzt den Eintrag).
export function setzeProfilInUrl(profil: string): void {
  if (typeof history === "undefined" || profilAusUrl() === profil) return;
  history.replaceState({ ansicht: route.ansicht }, "", baueUrl(route.ansicht, ortAusUrl(), profil));
}

// Beim ersten Aufruf die URL auf den Startzustand normalisieren (Ort + Profil).
export function initUrl(ort: string, profil: string): void {
  if (typeof history === "undefined") return;
  history.replaceState({ ansicht: route.ansicht }, "", baueUrl(route.ansicht, ort, profil));
}

// Zurueck/Vorwaerts im Browser folgt der Ansicht aus der URL.
if (typeof window !== "undefined") {
  window.addEventListener("popstate", () => {
    route.ansicht = ansichtAusUrl();
  });
}
