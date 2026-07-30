// Echte Wetterdaten des aktiven Ortes (aus dem Backend).
//
// Datenfrische pro Bereich: zeitkritische Daten (Warnungen, Blitze) werden haeufig
// aufgefrischt, traege Daten (Vorhersage, Luft, Pollen) selten. Jeder Bereich hat
// seinen eigenen Takt; die Kacheln lesen reaktiv aus diesem Store und aktualisieren
// sich dadurch von selbst.
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

type Basis = Pick<Komplett, "ort" | "aktuell" | "stunden" | "tage" | "sonne">;

// Auffrisch-Takte (ms) - abgestimmt auf die Cache-Stufen im Backend.
const TAKT_WARNUNGEN = 120_000; // 2 min - zeitkritisch
const TAKT_BLITZE = 90_000; // 1,5 min - zeitkritisch
const TAKT_BASIS = 600_000; // 10 min - Temperatur/Vorhersage
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

// --- Auffrischung je Bereich (aktualisiert nur die eigene Scheibe des Stores) ---

async function frischeBasis(): Promise<void> {
  try {
    const d = await hole<Basis>(`/wetter/basis/${wetter.slug}`);
    wetter.ort = d.ort.name;
    wetter.aktuell = d.aktuell;
    wetter.stunden = d.stunden;
    wetter.tage = d.tage;
    wetter.sonne = d.sonne;
    wetter.aktualisiert = Date.now();
  } catch {
    // Auffrischung fehlgeschlagen - alte Werte bleiben stehen.
  }
}

async function frischeWarnungen(): Promise<void> {
  try {
    wetter.warnungen = (await hole<Warnung[]>(`/wetter/warnungen/${wetter.slug}`)) ?? [];
  } catch {
    /* alte Werte behalten */
  }
}

async function frischeBlitze(): Promise<void> {
  try {
    wetter.blitze = await hole<Blitze | null>(`/wetter/blitze/${wetter.slug}`);
  } catch {
    /* alte Werte behalten */
  }
}

async function frischeLuft(): Promise<void> {
  try {
    wetter.luft = await hole<Luft | null>(`/wetter/luft/${wetter.slug}`);
  } catch {
    /* alte Werte behalten */
  }
}

async function frischePollen(): Promise<void> {
  try {
    wetter.pollen = await hole<Pollen | null>(`/wetter/pollen/${wetter.slug}`);
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
  } catch {
    // Backend/Quelle nicht erreichbar - Platzhalter bleiben sichtbar.
    wetter.geladen = false;
  }
  // Ab jetzt jeden Bereich in seinem eigenen Takt auffrischen.
  starteAuffrischung();
}
