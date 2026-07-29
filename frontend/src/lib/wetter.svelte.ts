// Echte Wetterdaten des aktiven Ortes (aus dem Backend).
import { hole } from "./api";
import type { Aktuell, Stunde, Tag } from "./typen";

interface Komplett {
  ort: { name: string; region: string };
  aktuell: Aktuell;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string };
}

export const wetter = $state<{
  slug: string;
  ort: string;
  aktuell: Aktuell | null;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string } | null;
  geladen: boolean;
}>({ slug: "koeln", ort: "Köln", aktuell: null, stunden: [], tage: [], sonne: null, geladen: false });

export async function ladeWetter(slug: string): Promise<void> {
  wetter.slug = slug;
  try {
    const d = await hole<Komplett>(`/weather/complete/${slug}`);
    wetter.ort = d.ort.name;
    wetter.aktuell = d.aktuell;
    wetter.stunden = d.stunden;
    wetter.tage = d.tage;
    wetter.sonne = d.sonne;
    wetter.geladen = true;
  } catch {
    // Backend/Quelle nicht erreichbar - Platzhalter bleiben sichtbar.
    wetter.geladen = false;
  }
}
