// Reaktiver Theme-Zustand (hell/dunkel) ueber [data-theme] am <html>-Element.
export const thema = $state<{ wert: "hell" | "dunkel" }>({ wert: "hell" });

export function setzeThema(wert: "hell" | "dunkel"): void {
  thema.wert = wert;
  document.documentElement.dataset.theme = wert;
}

export function themaUmschalten(): void {
  setzeThema(thema.wert === "hell" ? "dunkel" : "hell");
}
