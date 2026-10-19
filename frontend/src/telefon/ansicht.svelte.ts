// Was die Telefonansicht gerade zeigt: Reiter, aktiver Ort, offenes Blatt. Reiter, Ort und Profil
// stehen in der Adresse (?ansicht=&ort=&profil=), damit Neuladen und Lesezeichen dorthin führen.
import { lies, schreib } from "../kern/speicher";
import { uhr } from "../kern/uhr.svelte";
import type { TelefonKachel } from "../kern/gemeinsam";
import { geraet, setzeNacht, setzeUebersteuerung } from "./geraet.svelte";
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

/** Nach der Sonne am gewählten Ort: Nacht zwischen Untergang und Aufgang, und der nächste Wechsel. */
function sonnenlage(jetzt: number): { nacht: boolean; wechsel: number } | null {
  const tage = standVon(ansicht.ort).daten?.tage;
  const heute = tage?.[0];
  if (!heute?.sonnenaufgang || !heute.sonnenuntergang) return null;
  const auf = new Date(heute.sonnenaufgang).getTime();
  const unter = new Date(heute.sonnenuntergang).getTime();
  if (jetzt < auf) return { nacht: true, wechsel: auf };
  if (jetzt < unter) return { nacht: false, wechsel: unter };
  const morgen = tage?.[1]?.sonnenaufgang;
  return { nacht: true, wechsel: morgen ? new Date(morgen).getTime() : jetzt + 12 * 3_600_000 };
}

/** Nachtbetrieb aktiv: fest an oder aus, sonst nach der Sonne am Ort. Eine Umschaltung von Hand
 *  gilt bis zum nächsten Sonnenauf- oder -untergang, danach wieder die Zeitsteuerung. */
export function nachtAktiv(): boolean {
  if (geraet.nacht === "an") return true;
  if (geraet.nacht === "aus") return false;
  const jetzt = uhr.jetzt.getTime();
  const u = geraet.uebersteuerung;
  if (u && jetzt < u.bis) return u.nacht;
  return sonnenlage(jetzt)?.nacht ?? false;
}

/** Nachtbetrieb von Hand umschalten (Knopf im Kopf). Bei Zeitsteuerung bis zum nächsten Wechsel,
 *  sonst wird die feste Wahl getauscht. */
export function nachtUmschalten(): void {
  const jetzt = Date.now();
  const neu = !nachtAktiv();
  if (geraet.nacht !== "auto") {
    setzeNacht(neu ? "an" : "aus");
    return;
  }
  const lage = sonnenlage(jetzt);
  // Stimmt die Wahl wieder mit der Sonne überein, braucht es keine Übersteuerung mehr.
  if (lage && lage.nacht === neu) setzeUebersteuerung(null);
  else setzeUebersteuerung({ nacht: neu, bis: lage?.wechsel ?? jetzt + 12 * 3_600_000 });
}
