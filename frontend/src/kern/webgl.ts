// Karten zeichnen mit WebGL. Fehlt es (ältere Geräte, abgeschaltete Grafikbeschleunigung), wirft die
// Kartenbibliothek schon beim Anlegen; ohne diesen Schutz riss das die ganze Desktop-Ansicht mit (keine Orte,
// alles blieb bei "lädt"). Mit ihm zeigt die Karte einen Hinweis, alles andere läuft weiter.

export const OHNE_WEBGL = "Die Karte braucht WebGL; dieser Browser stellt es gerade nicht bereit.";

let moeglich: boolean | null = null;

export function webglMoeglich(): boolean {
  if (moeglich === null) {
    try {
      const flaeche = document.createElement("canvas");
      moeglich = Boolean(flaeche.getContext("webgl2") ?? flaeche.getContext("webgl"));
    } catch {
      moeglich = false;
    }
  }
  return moeglich;
}

/** Karte anlegen, wenn es geht; sonst null (WebGL fehlt oder die Bibliothek scheitert beim Anlegen). */
export function karteAnlegen<T>(anlegen: () => T): T | null {
  if (!webglMoeglich()) return null;
  try {
    return anlegen();
  } catch (fehler) {
    console.warn("Karte nicht angelegt:", fehler);
    return null;
  }
}

/** Fehlermeldungen der Karte: ein abgebrochener Bildabruf (AbortError, etwa wenn die Radarwiedergabe schneller zum
 *  nächsten Bild springt, als das vorige lädt) ist gewollt und keiner; alle anderen gehen wie bisher in die Konsole. */
export function kartenfehlerMelden(karte: { on: (art: "error", f: (e: { error?: unknown }) => void) => unknown }): void {
  karte.on("error", (e) => {
    if (e.error instanceof Error && e.error.name === "AbortError") return;
    console.error(e.error ?? e);
  });
}
