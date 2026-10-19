// Was die Telefonansicht gerade zeigt: Reiter, aktiver Ort, offenes Blatt. Reiter, Ort und Profil
// stehen in der Adresse (?ansicht=&ort=&profil=), damit Neuladen und Lesezeichen dorthin führen.
import { lies, schreib } from "../kern/speicher";
import { uhr } from "../kern/uhr.svelte";
import type { TelefonKachel } from "../kern/gemeinsam";
import { geraet } from "./geraet.svelte";
import { profile } from "./profil.svelte";
import { standVon } from "./wetter.svelte";

// Karte, Wetter und Gesundheit sind Seiten, zwischen denen man wischt; Mehr nur über die Leiste.
export type Reiter = "karte" | "wetter" | "gesundheit" | "mehr";
export const WISCHSEITEN: Reiter[] = ["karte", "wetter", "gesundheit"];
const REITER: Reiter[] = [...WISCHSEITEN, "mehr"];

export type Blatt = { art: "detail"; kachel: TelefonKachel } | { art: "warnungen" } | { art: "orte" } | { art: "schaukasten" };

const adresse = new URLSearchParams(location.search);

export const ansicht = $state<{ reiter: Reiter; ort: string; blatt: Blatt | null }>({
  reiter: REITER.includes(adresse.get("ansicht") as Reiter) ? (adresse.get("ansicht") as Reiter) : "wetter",
  ort: adresse.get("ort") || lies<string>("telefon.ort", ""),
  // ?blatt=schaukasten öffnet beim Start die Übersicht aller Kachelformen (auch zum Prüfen)
  blatt: adresse.get("blatt") === "schaukasten" ? { art: "schaukasten" } : null,
});

export const profilAusAdresse = adresse.get("profil");

export function zeige(reiter: Reiter): void {
  ansicht.reiter = reiter;
  ansicht.blatt = null;
}

/** Zur Nachbarseite wischen (Karte, Wetter, Gesundheit); am Rand passiert nichts. */
export function wischeSeite(richtung: 1 | -1): void {
  const i = WISCHSEITEN.indexOf(ansicht.reiter);
  if (i < 0) return;
  const ziel = WISCHSEITEN[i + richtung];
  if (ziel) zeige(ziel);
}

export function waehleOrt(slug: string): void {
  ansicht.ort = slug;
  schreib("telefon.ort", slug);
}

export function oeffne(blatt: Blatt): void {
  ansicht.blatt = blatt;
}

export function schliesse(): void {
  ansicht.blatt = null;
}

/** Adresse nachführen (ohne neuen Verlaufseintrag). */
export function adresseSpiegeln(): void {
  const p = new URLSearchParams();
  if (ansicht.reiter !== "wetter") p.set("ansicht", ansicht.reiter);
  if (ansicht.ort) p.set("ort", ansicht.ort);
  if (profile.aktivId) p.set("profil", profile.aktivId);
  const ziel = `${location.pathname}${p.size ? `?${p}` : ""}`;
  if (ziel !== `${location.pathname}${location.search}`) history.replaceState(null, "", ziel);
}

/** Nachtbetrieb aktiv: an, oder automatisch zwischen Sonnenuntergang und -aufgang am Ort. */
export function nachtAktiv(): boolean {
  if (geraet.nacht === "an") return true;
  if (geraet.nacht === "aus") return false;
  const heute = standVon(ansicht.ort).daten?.tage[0];
  if (!heute?.sonnenaufgang || !heute.sonnenuntergang) return false;
  const jetzt = uhr.jetzt.getTime();
  return jetzt < new Date(heute.sonnenaufgang).getTime() || jetzt > new Date(heute.sonnenuntergang).getTime();
}
