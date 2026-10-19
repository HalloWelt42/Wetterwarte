// Profile mit ihrem Telefon-Layout. Am Telefon wird nur gewählt, eingerichtet wird am Desktop.
// Die Liste liegt zusätzlich im Gerätespeicher, damit die Ansicht auch ohne Verbindung startet.
import { hole } from "../kern/api";
import { lies, schreib } from "../kern/speicher";
import type { TelefonLayout } from "../kern/gemeinsam";

export interface Profil {
  id: string;
  name: string;
  icon: string;
  ist_standard: boolean;
  telefon: TelefonLayout | null;
}

export const profile = $state<{ liste: Profil[]; aktivId: string; geladen: boolean }>({
  liste: lies<Profil[]>("telefon.profile", []),
  aktivId: "",
  geladen: false,
});

export function aktivesProfil(): Profil | undefined {
  return profile.liste.find((p) => p.id === profile.aktivId) ?? profile.liste.find((p) => p.ist_standard) ?? profile.liste[0];
}

export function waehleProfil(id: string): void {
  profile.aktivId = id;
  schreib("telefon.profil", id);
}

/** Profile laden; Vorrang für die Wahl: Adresse, dann Gerät, dann Standardprofil. */
export async function ladeProfile(ausAdresse: string | null): Promise<void> {
  profile.aktivId = ausAdresse || lies<string>("telefon.profil", "");
  try {
    profile.liste = await hole<Profil[]>("/layouts");
    schreib("telefon.profile", profile.liste);
  } catch {
    // ohne Verbindung bleibt die gemerkte Liste
  }
  if (!profile.liste.some((p) => p.id === profile.aktivId)) profile.aktivId = aktivesProfil()?.id ?? "";
  profile.geladen = true;
}
