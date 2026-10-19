// Geteilte, selbst-auffrischende Datenquellen je (Bereich, Ort).
//
// Grundlage der Widget-Isolation: Jedes Widget abonniert genau die Bereiche, die es
// braucht - fuer seinen eigenen Ort. Mehrere Widgets mit demselben (Bereich, Ort)
// teilen sich EINE Abfrage und EINEN Takt (Dedup, referenzgezaehlt): der Abruf startet
// beim ersten Abonnenten und stoppt beim letzten.
//
// Weil eine Quelle fest an ihren Ort gebunden ist, kann die Antwort eines Ortes nie
// die Daten eines anderen ueberschreiben - die Ortswechsel-Race entfaellt by-design.
import { holeMitMeta } from "./api";

// Auffrisch-Takte (ms) je Bereich - abgestimmt auf die Cache-Stufen im Backend.
const TAKTE: Record<string, number> = {
  basis: 300_000, // 5 min - Temperatur/Vorhersage/Nowcast (wie die Frische im Backend)
  warnungen: 120_000, // 2 min - zeitkritisch
  blitze: 90_000, // 1,5 min - zeitkritisch
  luft: 900_000, // 15 min - traege
  pollen: 3_600_000, // 1 h - sehr traege
};
const STANDARD_TAKT = 600_000;

/** laedt: noch nie geladen; ok: frisch; alt: letzter guter Stand (Quelle gerade weg);
 *  fehlt: keine verwertbaren Daten. Erfundene Ersatzwerte gibt es nie. */
export type Zustand = "laedt" | "ok" | "alt" | "fehlt";

export interface Quelle {
  data: unknown; // zuletzt geladene Daten des Bereichs (null bis zum ersten Erfolg)
  aktualisiert: number; // Zeitstempel (ms) der letzten erfolgreichen Abfrage
  zustand: Zustand;
  stand: string | null; // Zeitpunkt der Daten (ISO), vom Server
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
    const { data, meta } = await holeMitMeta<unknown>(`/wetter/${e.bereich}/${e.ort}`);
    e.quelle.data = data;
    e.quelle.zustand = meta.status ?? (data == null ? "fehlt" : "ok");
    e.quelle.stand = meta.stand ?? null;
    e.quelle.aktualisiert = Date.now();
  } catch {
    // Server nicht erreichbar: vorhandene Werte bleiben, gelten aber als alt.
    e.quelle.zustand = e.quelle.data == null ? "fehlt" : "alt";
  }
}

/** Bereich fuer einen Ort abonnieren. Startet Abruf + Takt beim ersten Abonnenten. */
export function abonniere(bereich: string, ort: string): Quelle {
  const k = schluessel(bereich, ort);
  let e = eintraege.get(k);
  if (!e) {
    const quelle = $state<Quelle>({ data: null, aktualisiert: 0, zustand: "laedt", stand: null });
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

/** Alle Quellen auffrischen, deren Takt seit dem letzten Abruf verstrichen ist (etwa beim
 *  Zurückkehren in die App: Takte schlafen im Hintergrund, die Werte sind dann veraltet). */
export function frischeVeraltete(): void {
  const jetzt = Date.now();
  for (const e of eintraege.values()) {
    if (jetzt - e.quelle.aktualisiert >= (TAKTE[e.bereich] ?? STANDARD_TAKT)) void lade(e);
  }
}

/** Takt eines Bereichs (ms), etwa für die Anzeige der Datenfrische. */
export function taktVon(bereich: string): number {
  return TAKTE[bereich] ?? STANDARD_TAKT;
}
