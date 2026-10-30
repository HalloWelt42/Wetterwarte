// Neue Fassung auf dem Server: nie ein hartes Neuladen verlangen.
// Die Startseite kommt ohne Zwischenspeicher, Skripte und Gestaltung tragen Prüfsummen im Namen. Meldet der Server
// eine andere Fassung als die eingebaute, lädt die Seite von selbst neu: in den ersten Sekunden nach dem Start sofort,
// später beim nächsten Ortswechsel (Ansicht, Ort, Profil, Zurück/Vor) oder wenn das Fenster wieder nach vorn kommt.
// Nie, solange ein Teil der Oberfläche meldet, dass ein Neuladen etwas abbräche (offener Dialog, Ortssuche, laufende
// Radar-Wiedergabe); dann wartet sie bis danach. Dazwischen steht ein Band mit Knopf. Je Server-Fassung nur ein
// selbsttätiger Versuch (Merker in der Sitzung), damit ein hängender Zwischenspeicher keine Schleife auslöst. Neu geladen
// wird nur, wenn der Server unmittelbar davor antwortet; ohne Verbindung bleibt die laufende Fassung stehen.
import { untrack } from "svelte";
import { SvelteSet } from "svelte/reactivity";
import { hole } from "./api";

export const OBERFLAECHE_FASSUNG = __FASSUNG__;
const MERKER = "wetterwarte.neu_geladen";
const START_FENSTER_MS = 10_000;
const PRUEFEN_MS = 60_000;

export const fassung = $state<{ neu: string | null }>({ neu: null });

export type Anlass = "start" | "takt" | "ortswechsel" | "sichtbar";

// Jeder Teil der Oberfläche meldet hier, ob ein Neuladen gerade etwas abbräche (reaktiv, damit das Band mitzieht).
const taetigkeiten = new SvelteSet<() => boolean>();

// Meldet eine Prüfung "ist gerade etwas im Gange" an; die Rückgabe meldet sie wieder ab (passt zu onMount).
export function neuLadenAufhalten(beschaeftigt: () => boolean): () => void {
  taetigkeiten.add(beschaeftigt);
  return () => {
    taetigkeiten.delete(beschaeftigt);
  };
}

// Nichts, was ein Neuladen abbrechen würde.
export function ruhig(): boolean {
  for (const beschaeftigt of taetigkeiten) if (beschaeftigt()) return false;
  return true;
}

function erlaubt(neu: string): boolean {
  try {
    if (sessionStorage.getItem(MERKER) === neu) return false;
    sessionStorage.setItem(MERKER, neu);
  } catch {
    // ohne Sitzungsspeicher kein Merker: dann lieber einmal laden als nie
  }
  return true;
}

// Ob der Anlass ein Neuladen erlaubt (eine neue Fassung wartet, nichts ist im Gange, beim Start nur anfangs).
function anlassPasst(anlass: Anlass): boolean {
  if (!fassung.neu || anlass === "takt" || !ruhig()) return false;
  return anlass !== "start" || performance.now() <= START_FENSTER_MS;
}

// Ein Wechsel von Ansicht, Ort oder Profil: neu laden, wenn eine neue Fassung wartet und der Server erreichbar ist.
// Ohne Abhängigkeit gelesen: ruft ein $effect dies beim Wechsel auf, darf das Eintreffen einer neuen Fassung (oder
// das Ende einer Tätigkeit) den Effekt nicht erneut auslösen, sonst lüde die Seite ohne Wechsel mitten in der Arbeit.
export function vielleichtNeuLaden(anlass: Anlass): void {
  if (untrack(() => anlassPasst(anlass))) void neuLadenWennErreichbar();
}

// Fassung des Servers holen und merken; ohne Verbindung null (dann bleibt der letzte Stand stehen).
async function serverFassung(): Promise<string | null> {
  try {
    const server = (await hole<{ version: string }>("/health")).version;
    fassung.neu = server !== OBERFLAECHE_FASSUNG ? server : null;
    return server;
  } catch {
    return null;
  }
}

// Neu laden nur, wenn der Server gerade antwortet: ohne Verbindung endete das Neuladen auf der Fehlerseite des
// Browsers, und der Wechsel, der es ausgelöst hat (etwa "Große Karte öffnen"), wäre verloren. Die Ansicht ist zu
// diesem Zeitpunkt schon gewechselt; das Neuladen landet dort.
async function neuLadenWennErreichbar(): Promise<void> {
  if ((await serverFassung()) !== null) neuLaden();
}

function neuLaden(): void {
  const neu = fassung.neu;
  if (neu && ruhig() && erlaubt(neu)) location.reload();
}

export async function fassungPruefen(anlass: Anlass): Promise<void> {
  if ((await serverFassung()) === null) return; // ohne Verbindung kein Vergleich; der nächste Takt versucht es wieder
  if (anlassPasst(anlass)) neuLaden();
}

function sichtbar(): void {
  if (document.visibilityState === "visible") void fassungPruefen("sichtbar");
}

export function fassungVerfolgen(): () => void {
  void fassungPruefen("start");
  const takt = setInterval(() => void fassungPruefen("takt"), PRUEFEN_MS);
  document.addEventListener("visibilitychange", sichtbar);
  return () => {
    clearInterval(takt);
    document.removeEventListener("visibilitychange", sichtbar);
  };
}
