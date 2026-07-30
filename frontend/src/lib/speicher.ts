// Kleiner localStorage-Helfer fuer gemerkte UI-Einstellungen (Basiskarte,
// Overlays, Groessen, Panel-Zustaende ...). Faellt still auf den Standard
// zurueck, wenn localStorage nicht verfuegbar ist (z.B. privater Modus).
export function lies<T>(schluessel: string, standard: T): T {
  try {
    const roh = localStorage.getItem(`wetterwarte.${schluessel}`);
    return roh === null ? standard : (JSON.parse(roh) as T);
  } catch {
    return standard;
  }
}

export function schreib(schluessel: string, wert: unknown): void {
  try {
    localStorage.setItem(`wetterwarte.${schluessel}`, JSON.stringify(wert));
  } catch {
    // nicht speicherbar - dann eben nicht merken
  }
}
