// Ortsliste des Nutzers - datengetrieben aus der Datenbank (per Suche gepflegt).
import { hole, sende } from "./api";

export interface Ort {
  id: string;
  slug: string;
  name: string;
  region: string;
  land: string;
  lat: number;
  lon: number;
  zeitzone: string;
  reihenfolge: number;
  ist_start: boolean;
}

export interface Treffer {
  name: string;
  region: string;
  land: string;
  lat: number;
  lon: number;
  zeitzone?: string;
}

/** IANA-Zeitzone eines Ortes (leer = unbekannt, dann lokale Geraetezeit). */
export function zeitzoneFuer(slug: string): string {
  return orteState.liste.find((o) => o.slug === slug)?.zeitzone || "";
}

export const orteState = $state<{ liste: Ort[] }>({ liste: [] });

export async function ladeOrte(): Promise<void> {
  try {
    orteState.liste = await hole<Ort[]>("/orte");
  } catch {
    // Ohne Backend bleibt die Liste leer.
  }
}

export async function sucheOrte(q: string): Promise<Treffer[]> {
  try {
    return await hole<Treffer[]>(`/orte/suche?q=${encodeURIComponent(q)}`);
  } catch {
    return [];
  }
}

export async function fuegeOrtHinzu(t: Treffer): Promise<Ort | null> {
  try {
    const neu = await sende<Ort>("/orte", "POST", t);
    await ladeOrte();
    return neu;
  } catch {
    return null;
  }
}

export async function entferneOrt(id: string): Promise<void> {
  try {
    await sende(`/orte/${id}`, "DELETE");
    await ladeOrte();
  } catch {
    // Fehler still - Liste bleibt unveraendert.
  }
}

export function startOrt(): Ort | undefined {
  return orteState.liste.find((o) => o.ist_start) ?? orteState.liste[0];
}

export async function sortiereOrte(ids: string[]): Promise<void> {
  try {
    await sende("/orte/reihenfolge", "PUT", { ids });
  } catch {
    // Fehler still - die lokale Reihenfolge bleibt trotzdem stehen.
  }
}
