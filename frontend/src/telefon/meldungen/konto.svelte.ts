// Dieses Gerät beim Server (docs/WARNUNGEN.md): Kennung im Gerätespeicher, Meldeeinstellungen, Push-Abo und
// Protokoll liegen in der Datenbank, weil der Melder auch bei geschlossener App wissen muss, was das Gerät will.
// Angelegt wird das Gerät erst, wenn es Mitteilungen oder Ansagen einschaltet.
import { hole, sende } from "../../kern/api";
import type { Meldeart } from "../../kern/gemeinsam";
import { lies, schreib } from "../../kern/speicher";

export interface Nachtruhe {
  an: boolean;
  von: number;
  bis: number;
  ab_stufe: number;
}

export interface Meldeeinstellungen {
  orte: string[];
  arten: Meldeart[];
  vorlauf_min: number;
  niederschlag_ab: number;
  wind_ab: number;
  nachtruhe: Nachtruhe;
}

export interface Protokolleintrag {
  zeit: string;
  kanal: "push" | "ansage";
  ort: string;
  art: Meldeart;
  stufe: number;
  titel: string;
  text: string;
  zugestellt: boolean;
}

export interface GeraetAntwort {
  id: string;
  einstellungen: Meldeeinstellungen;
  push: boolean;
  protokoll: Protokolleintrag[];
}

const SCHLUESSEL = "telefon.geraet";

export const konto = $state<{ id: string | null; daten: GeraetAntwort | null; fehler: string }>({
  id: lies<string | null>(SCHLUESSEL, null),
  daten: null,
  fehler: "",
});

function uebernehmen(daten: GeraetAntwort): GeraetAntwort {
  konto.daten = daten;
  konto.id = daten.id;
  konto.fehler = "";
  schreib(SCHLUESSEL, daten.id);
  return daten;
}

/** Stand vom Server holen; kennt er das Gerät nicht mehr, wird die Kennung vergessen. */
export async function ladeKonto(): Promise<void> {
  if (!konto.id) return;
  try {
    uebernehmen(await hole<GeraetAntwort>(`/geraete/${konto.id}`));
  } catch (e) {
    if (String(e).includes(": 404")) {
      konto.id = null;
      konto.daten = null;
      schreib(SCHLUESSEL, null);
    } else konto.fehler = "Der Server ist gerade nicht erreichbar.";
  }
}

/** Gerät anlegen, falls es noch keins gibt; der gezeigte Ort ist für Mitteilungen vorgewählt. */
export async function sicheresKonto(ort: string): Promise<GeraetAntwort> {
  if (konto.daten) return konto.daten;
  if (konto.id) await ladeKonto();
  if (konto.daten) return konto.daten;
  return uebernehmen(await sende<GeraetAntwort>("/geraete", "POST", { ort: ort || null }));
}

export async function einstellen(teil: Partial<Meldeeinstellungen>): Promise<void> {
  if (!konto.daten) return;
  const neu = { ...konto.daten.einstellungen, ...teil };
  konto.daten.einstellungen = neu; // sofort sichtbar, der Server bestätigt
  try {
    uebernehmen(await sende<GeraetAntwort>(`/geraete/${konto.daten.id}/einstellungen`, "PUT", neu));
  } catch {
    konto.fehler = "Die Einstellung konnte nicht gespeichert werden.";
    await ladeKonto();
  }
}

export async function aboSetzen(abo: PushSubscriptionJSON): Promise<void> {
  if (!konto.id) return;
  uebernehmen(await sende<GeraetAntwort>(`/geraete/${konto.id}/push`, "PUT", abo));
}

export async function aboLoeschen(): Promise<void> {
  if (!konto.id) return;
  uebernehmen(await sende<GeraetAntwort>(`/geraete/${konto.id}/push`, "DELETE"));
}

export async function probe(): Promise<"ok" | "weg" | "fehler" | "kein_abo"> {
  if (!konto.id) return "kein_abo";
  const { ergebnis } = await sende<{ ergebnis: "ok" | "weg" | "fehler" | "kein_abo" }>(`/geraete/${konto.id}/probe`, "POST");
  await ladeKonto();
  return ergebnis;
}
