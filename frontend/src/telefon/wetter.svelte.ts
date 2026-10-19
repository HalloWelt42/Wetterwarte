// Wetterdaten der Telefonansicht: je Ort ein Abruf von /wetter/kompakt/{ort} (alles in einem,
// rund 3 KB). Der aktive Ort frischt alle 5 Minuten auf und sofort beim Zurückkehren in die App.
// Der letzte Stand je Ort liegt im Gerätespeicher und erscheint sofort beim Start, auch ohne
// Verbindung; dann sagt der Zustand "alt", nie werden Werte erfunden.
import { holeMitMeta } from "../kern/api";
import { lies, schreib } from "../kern/speicher";
import type { Kompakt } from "./typen";

export const TAKT_MS = 5 * 60_000;

export type Zustand = "laedt" | "ok" | "alt" | "fehlt";

export interface OrtStand {
  daten: Kompakt | null;
  zustand: Zustand;
  geholt: number; // Zeitpunkt (ms) des letzten erfolgreichen Abrufs
}

export const staende = $state<Record<string, OrtStand>>({});
const laufend = new Set<string>();

function gemerkt(slug: string): OrtStand {
  const g = lies<{ daten: Kompakt; geholt: number } | null>(`telefon.stand.${slug}`, null);
  return g ? { daten: g.daten, zustand: "alt", geholt: g.geholt } : { daten: null, zustand: "laedt", geholt: 0 };
}

const LEER: OrtStand = { daten: null, zustand: "laedt", geholt: 0 };

/** Stand eines Orts lesen (auch in abgeleiteten Werten; legt nichts an). */
export function standVon(slug: string): OrtStand {
  return staende[slug] ?? LEER;
}

/** Eintrag anlegen, mit dem gemerkten Stand aus dem Gerätespeicher (nur außerhalb von $derived). */
function bereite(slug: string): OrtStand {
  if (!staende[slug]) staende[slug] = gemerkt(slug);
  return staende[slug];
}

export async function lade(slug: string): Promise<void> {
  if (!slug || laufend.has(slug)) return;
  laufend.add(slug);
  const stand = bereite(slug);
  try {
    const { data } = await holeMitMeta<Kompakt>(`/wetter/kompakt/${slug}`);
    stand.daten = data;
    stand.geholt = Date.now();
    stand.zustand = data.bereiche.basis.status === "fehlt" ? "fehlt" : "ok";
    schreib(`telefon.stand.${slug}`, { daten: data, geholt: stand.geholt });
  } catch {
    stand.zustand = stand.daten ? "alt" : "fehlt";
  } finally {
    laufend.delete(slug);
  }
}

/** Laden, wenn der Stand älter als der Takt ist (oder noch keiner da ist). */
export function ladeWennAlt(slug: string): void {
  if (!slug) return;
  const s = bereite(slug);
  if (Date.now() - s.geholt >= TAKT_MS || s.zustand !== "ok") void lade(slug);
}

/** Aktiven Ort im Takt und beim Zurückkehren auffrischen. Rückgabe beendet das Verfolgen. */
export function verfolge(aktiv: () => string): () => void {
  const takt = setInterval(() => void lade(aktiv()), TAKT_MS);
  const sichtbar = () => {
    if (document.visibilityState === "visible") ladeWennAlt(aktiv());
  };
  document.addEventListener("visibilitychange", sichtbar);
  window.addEventListener("online", sichtbar);
  return () => {
    clearInterval(takt);
    document.removeEventListener("visibilitychange", sichtbar);
    window.removeEventListener("online", sichtbar);
  };
}
