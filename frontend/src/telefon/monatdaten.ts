// Daten des Monatsvergleichs für Kachel und Blatt: Klimamittel des Orts und die gemessenen Monatswerte
// des Jahres. Je Ort und Jahr eine Stunde zwischengespeichert, Kachel und Blatt teilen den Abruf.
import { hole } from "../kern/api";

// Aufgezeichnete Niederschlagsgröße (Monatssumme in mm); ohne Werte entfällt der Niederschlag.
export const NIEDERSCHLAG = "niederschlag";

export interface KlimaMonat {
  monat: number;
  temp: number | null;
  niederschlag: number | null;
}

export interface Klima {
  monate: KlimaMonat[];
  von: number;
  bis: number;
  jahresniederschlag: number | null;
}

export interface Messmonat {
  monat: number;
  mittel: number | null;
  summe: number | null;
  anzahl: number;
}

export interface Monatsdaten {
  klima: Klima;
  temperatur: Messmonat[];
  niederschlag: Messmonat[] | null; // null: wird für diesen Ort nicht aufgezeichnet
}

export const STUNDE_MS = 3_600_000;
const speicher = new Map<string, { zeit: number; daten: Promise<Monatsdaten> }>();

async function lade(ort: string, jahr: number): Promise<Monatsdaten> {
  const pfad = encodeURIComponent(ort);
  const reihe = (variable: string) =>
    hole<{ monate: Messmonat[] }>(`/wetter/jahresmesswerte/${pfad}?jahr=${jahr}&variable=${variable}`).then((d) => d.monate);
  const [klima, temperatur, niederschlag] = await Promise.all([
    hole<Klima>(`/wetter/klima/${pfad}`),
    reihe("temperatur"),
    reihe(NIEDERSCHLAG).catch(() => null),
  ]);
  return { klima, temperatur, niederschlag: niederschlag?.some((m) => m.summe !== null) ? niederschlag : null };
}

/** Monatsdaten eines Orts und Jahres; ein fehlgeschlagener Abruf wird nicht gemerkt. */
export function holeMonatsdaten(ort: string, jahr: number): Promise<Monatsdaten> {
  const k = `${ort}:${jahr}`;
  const e = speicher.get(k);
  if (e && Date.now() - e.zeit < STUNDE_MS) return e.daten;
  const daten = lade(ort, jahr);
  speicher.set(k, { zeit: Date.now(), daten });
  daten.catch(() => {
    if (speicher.get(k)?.daten === daten) speicher.delete(k);
  });
  return daten;
}
