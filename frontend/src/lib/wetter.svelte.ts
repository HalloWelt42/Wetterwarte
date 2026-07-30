// Echte Wetterdaten des aktiven Ortes (aus dem Backend).
//
// Datenfrische pro Bereich: zeitkritische Daten (Warnungen, Blitze) werden haeufig
// aufgefrischt, traege Daten (Vorhersage, Luft, Pollen) selten. Jeder Bereich hat
// seinen eigenen Takt; die Kacheln lesen reaktiv aus diesem Store und aktualisieren
// sich dadurch von selbst.
//
// Ortswechsel-Sicherheit: jede Abfrage merkt sich den Ziel-Ort und schreibt ihr
// Ergebnis nur zurueck, wenn der Ort inzwischen nicht gewechselt hat - sonst wuerde
// eine langsame Antwort eines alten Ortes den neuen ueberschreiben.
import { hole } from "./api";
import { schreib } from "./speicher";
import type { Aktuell, Blitze, Luft, Nowcast, Pollen, Stunde, Tag, Warnung } from "./typen";

interface Komplett {
  ort: { name: string; region: string };
  aktuell: Aktuell;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string };
  warnungen: Warnung[];
  luft: Luft | null;
  nowcast: Nowcast | null;
  blitze: Blitze | null;
  pollen: Pollen | null;
}

type Basis = Pick<Komplett, "ort" | "aktuell" | "stunden" | "tage" | "sonne" | "nowcast">;

// Auffrisch-Takte (ms) - abgestimmt auf die Cache-Stufen im Backend.
const TAKT_WARNUNGEN = 120_000; // 2 min - zeitkritisch
const TAKT_BLITZE = 90_000; // 1,5 min - zeitkritisch
const TAKT_BASIS = 600_000; // 10 min - Temperatur/Vorhersage/Nowcast
const TAKT_LUFT = 900_000; // 15 min - traege
const TAKT_POLLEN = 3_600_000; // 1 h - sehr traege

export const wetter = $state<{
  slug: string;
  ort: string;
  aktuell: Aktuell | null;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string } | null;
  warnungen: Warnung[];
  luft: Luft | null;
  nowcast: Nowcast | null;
  blitze: Blitze | null;
  pollen: Pollen | null;
  geladen: boolean;
  aktualisiert: number; // Zeitstempel (ms) der letzten Basis-Auffrischung
}>({
  slug: "",
  ort: "",
  aktuell: null,
  stunden: [],
  tage: [],
  sonne: null,
  warnungen: [],
  luft: null,
  nowcast: null,
  blitze: null,
  pollen: null,
  geladen: false,
  aktualisiert: 0,
});

// --- Auffrischung je Bereich ---
// Jede Funktion haelt den Ziel-Slug fest und schreibt nur zurueck, wenn der Ort
// nach dem await noch derselbe ist (Schutz vor Ueberschreiben beim Ortswechsel).

async function frischeBasis(): Promise<void> {
  const slug = wetter.slug;
  if (!slug) return;
  try {
    const d = await hole<Basis>(`/wetter/basis/${slug}`);
    if (wetter.slug !== slug) return;
    wetter.ort = d.ort.name;
    wetter.aktuell = d.aktuell;
    wetter.stunden = d.stunden;
    wetter.tage = d.tage;
    wetter.sonne = d.sonne;
    wetter.nowcast = d.nowcast ?? null;
    wetter.geladen = true; // erfolgreiche Auffrischung hebt einen fehlgeschlagenen Erststart auf
    wetter.aktualisiert = Date.now();
  } catch {
    /* alte Werte behalten */
  }
}

async function frischeWarnungen(): Promise<void> {
  const slug = wetter.slug;
  if (!slug) return;
  try {
    const w = (await hole<Warnung[]>(`/wetter/warnungen/${slug}`)) ?? [];
    if (wetter.slug !== slug) return;
    wetter.warnungen = w;
  } catch {
    /* alte Werte behalten */
  }
}

async function frischeBlitze(): Promise<void> {
  const slug = wetter.slug;
  if (!slug) return;
  try {
    const b = await hole<Blitze | null>(`/wetter/blitze/${slug}`);
    if (wetter.slug !== slug) return;
    wetter.blitze = b;
  } catch {
    /* alte Werte behalten */
  }
}

async function frischeLuft(): Promise<void> {
  const slug = wetter.slug;
  if (!slug) return;
  try {
    const l = await hole<Luft | null>(`/wetter/luft/${slug}`);
    if (wetter.slug !== slug) return;
    wetter.luft = l;
  } catch {
    /* alte Werte behalten */
  }
}

async function frischePollen(): Promise<void> {
  const slug = wetter.slug;
  if (!slug) return;
  try {
    const p = await hole<Pollen | null>(`/wetter/pollen/${slug}`);
    if (wetter.slug !== slug) return;
    wetter.pollen = p;
  } catch {
    /* alte Werte behalten */
  }
}

// --- Taktgeber ---

let takte: ReturnType<typeof setInterval>[] = [];

function stoppeAuffrischung(): void {
  takte.forEach(clearInterval);
  takte = [];
}

function starteAuffrischung(): void {
  stoppeAuffrischung();
  takte.push(setInterval(frischeWarnungen, TAKT_WARNUNGEN));
  takte.push(setInterval(frischeBlitze, TAKT_BLITZE));
  takte.push(setInterval(frischeBasis, TAKT_BASIS));
  takte.push(setInterval(frischeLuft, TAKT_LUFT));
  takte.push(setInterval(frischePollen, TAKT_POLLEN));
}

// Beim Zurueckkehren zum Tab die zeitkritischen Bereiche sofort auffrischen.
if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && wetter.slug) {
      void frischeWarnungen();
      void frischeBlitze();
      void frischeBasis();
    }
  });
}

export async function ladeWetter(slug: string): Promise<void> {
  wetter.slug = slug;
  schreib("ort.aktiv", slug); // zuletzt betrachteten Ort merken
  try {
    const d = await hole<Komplett>(`/wetter/complete/${slug}`);
    if (wetter.slug === slug) {
      wetter.ort = d.ort.name;
      wetter.aktuell = d.aktuell;
      wetter.stunden = d.stunden;
      wetter.tage = d.tage;
      wetter.sonne = d.sonne;
      wetter.warnungen = d.warnungen ?? [];
      wetter.luft = d.luft ?? null;
      wetter.nowcast = d.nowcast ?? null;
      wetter.blitze = d.blitze ?? null;
      wetter.pollen = d.pollen ?? null;
      wetter.geladen = true;
      wetter.aktualisiert = Date.now();
    }
  } catch {
    // Backend/Quelle nicht erreichbar - Platzhalter bleiben sichtbar.
    if (wetter.slug === slug) wetter.geladen = false;
  }
  // Ab jetzt jeden Bereich in seinem eigenen Takt auffrischen (nur fuer den
  // weiterhin aktiven Ort; bei zwischenzeitlichem Wechsel uebernimmt der neue Aufruf).
  if (wetter.slug === slug) starteAuffrischung();
}
