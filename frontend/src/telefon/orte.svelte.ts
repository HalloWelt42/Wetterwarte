// Orte für das Telefon: dieselbe Liste wie am Desktop (kern/orte), zusätzlich im Gerätespeicher,
// damit die Ansicht auch ohne Verbindung mit den bekannten Orten startet.
import { ladeOrte, orteState, startOrt, type Ort } from "../kern/orte.svelte";
import { lies, schreib } from "../kern/speicher";

export async function ladeOrteTelefon(): Promise<void> {
  await ladeOrte();
  if (orteState.liste.length) schreib("telefon.orte", orteState.liste);
  else orteState.liste = lies<Ort[]>("telefon.orte", []);
}

/** Gültiger Ort: der gewünschte, wenn es ihn gibt, sonst der Startort. */
export function gueltigerOrt(wunsch: string): string {
  return orteState.liste.some((o) => o.slug === wunsch) ? wunsch : (startOrt()?.slug ?? "");
}

/** Nachbarort in der Reihenfolge der Liste (zum Wischen über dem Kopf). */
export function nachbarOrt(slug: string, richtung: 1 | -1): string {
  const liste = orteState.liste;
  const i = liste.findIndex((o) => o.slug === slug);
  if (i < 0 || !liste.length) return slug;
  return liste[(i + richtung + liste.length) % liste.length].slug;
}
