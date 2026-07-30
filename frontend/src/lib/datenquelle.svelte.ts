// Geteilte, selbst-auffrischende Datenquellen je (Bereich, Ort).
//
// Grundlage der Widget-Isolation: Jedes Widget abonniert genau die Bereiche, die es
// braucht - fuer seinen eigenen Ort. Mehrere Widgets mit demselben (Bereich, Ort)
// teilen sich EINE Abfrage und EINEN Takt (Dedup, referenzgezaehlt): der Abruf startet
// beim ersten Abonnenten und stoppt beim letzten.
//
// Weil eine Quelle fest an ihren Ort gebunden ist, kann die Antwort eines Ortes nie
// die Daten eines anderen ueberschreiben - die Ortswechsel-Race entfaellt by-design.
import { hole } from "./api";

// Auffrisch-Takte (ms) je Bereich - abgestimmt auf die Cache-Stufen im Backend.
const TAKTE: Record<string, number> = {
  basis: 600_000, // 10 min - Temperatur/Vorhersage/Nowcast
  warnungen: 120_000, // 2 min - zeitkritisch
  blitze: 90_000, // 1,5 min - zeitkritisch
  luft: 900_000, // 15 min - traege
  pollen: 3_600_000, // 1 h - sehr traege
};
const STANDARD_TAKT = 600_000;
const ZEITKRITISCH = new Set(["warnungen", "blitze"]);

export interface Quelle {
  data: unknown; // zuletzt geladene Daten des Bereichs (null bis zum ersten Erfolg)
  aktualisiert: number; // Zeitstempel (ms) der letzten erfolgreichen Abfrage
}

interface Eintrag {
  quelle: Quelle;
  refs: number;
  timer: ReturnType<typeof setInterval> | null;
  bereich: string;
  ort: string;
}

const eintraege = new Map<string, Eintrag>();

function schluessel(bereich: string, ort: string): string {
  return `${bereich}:${ort}`;
}

async function lade(e: Eintrag): Promise<void> {
  try {
    const d = await hole<unknown>(`/wetter/${e.bereich}/${e.ort}`);
    e.quelle.data = d;
    e.quelle.aktualisiert = Date.now();
  } catch {
    // Abruf fehlgeschlagen - alte Werte behalten.
  }
}

/** Bereich fuer einen Ort abonnieren. Startet Abruf + Takt beim ersten Abonnenten. */
export function abonniere(bereich: string, ort: string): Quelle {
  const k = schluessel(bereich, ort);
  let e = eintraege.get(k);
  if (!e) {
    const quelle = $state<Quelle>({ data: null, aktualisiert: 0 });
    e = { quelle, refs: 0, timer: null, bereich, ort };
    eintraege.set(k, e);
    void lade(e);
    e.timer = setInterval(() => void lade(e!), TAKTE[bereich] ?? STANDARD_TAKT);
  }
  e.refs += 1;
  return e.quelle;
}

/** Abo aufgeben. Stoppt Abruf + Takt, wenn kein Abonnent mehr uebrig ist. */
export function gibFrei(bereich: string, ort: string): void {
  const k = schluessel(bereich, ort);
  const e = eintraege.get(k);
  if (!e) return;
  e.refs -= 1;
  if (e.refs <= 0) {
    if (e.timer) clearInterval(e.timer);
    eintraege.delete(k);
  }
}

/** Zeitkritische Bereiche aller aktiven Quellen sofort auffrischen (z.B. bei Tab-Rueckkehr). */
export function frischeZeitkritisch(): void {
  for (const e of eintraege.values()) {
    if (ZEITKRITISCH.has(e.bereich)) void lade(e);
  }
}
