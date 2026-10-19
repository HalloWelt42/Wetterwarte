// Zustand des Telefon-Editors: welches Profil, welche Seite, welche Kachel gewählt, Vorschau.
// Gespeichert wird nach jeder Änderung über PUT /layouts/{id}; das Backend prüft gegen den Katalog.
import { sende } from "../../kern/api";
import { kachelId } from "../../kern/kennung";
import { telefonKatalog, type TelefonKachel, type TelefonLayout } from "../../kern/gemeinsam";
import { layoutState, type Layout } from "../layout.svelte";
import { freieLage, groesse, verdichte, verschiebe } from "./raster";

export const editor = $state<{
  profilId: string;
  seite: string;
  gewaehlt: string | null;
  breite: number;
  nacht: boolean;
  fehler: string;
  speichert: boolean;
}>({
  profilId: "",
  seite: "wetter",
  gewaehlt: null,
  breite: 390,
  nacht: false,
  fehler: "",
  speichert: false,
});

export function profil(): Layout | undefined {
  return layoutState.liste.find((l) => l.id === (editor.profilId || layoutState.aktivId));
}

export function kacheln(): TelefonKachel[] {
  return profil()?.telefon?.seiten[editor.seite] ?? [];
}

export function gewaehlteKachel(): TelefonKachel | undefined {
  return kacheln().find((k) => k.id === editor.gewaehlt);
}

async function speichere(neu: TelefonKachel[]): Promise<void> {
  const p = profil();
  if (!p) return;
  const telefon: TelefonLayout = { seiten: { ...(p.telefon?.seiten ?? {}), [editor.seite]: neu } };
  const vorher = p.telefon;
  p.telefon = telefon; // sofort zeigen; bei Ablehnung zurück
  editor.speichert = true;
  editor.fehler = "";
  try {
    await sende(`/layouts/${p.id}`, "PUT", { telefon });
  } catch (fehler) {
    p.telefon = vorher;
    editor.fehler = `Nicht gespeichert: ${(fehler as Error).message}`;
  } finally {
    editor.speichert = false;
  }
}

export function hinzufuegen(typ: string): void {
  const def = telefonKatalog.typen[typ];
  if (!def) return;
  const [w, h] = def.groessen[0].split("x").map(Number);
  const lage = freieLage(kacheln(), w, h);
  const neu: TelefonKachel = { id: kachelId(typ), typ, ...lage, w, h, conf: {} };
  editor.gewaehlt = neu.id;
  void speichere(verdichte([...kacheln(), neu]));
}

export function bewege(id: string, x: number, y: number): void {
  void speichere(verschiebe(kacheln(), id, x, y));
}

export function setzeGroesse(id: string, w: number, h: number): void {
  void speichere(groesse(kacheln(), id, w, h));
}

export function setzeEinstellung(id: string, schluessel: string, wert: unknown): void {
  void speichere(kacheln().map((k) => (k.id === id ? { ...k, conf: { ...k.conf, [schluessel]: wert } } : k)));
}

export function entferne(id: string): void {
  if (editor.gewaehlt === id) editor.gewaehlt = null;
  void speichere(verdichte(kacheln().filter((k) => k.id !== id)));
}

export async function vorlageWiederherstellen(): Promise<void> {
  const p = profil();
  if (!p) return;
  try {
    const neu = await sende<Layout>(`/layouts/${p.id}/telefon-vorlage`, "POST");
    p.telefon = neu.telefon;
    editor.gewaehlt = null;
  } catch (fehler) {
    editor.fehler = `Vorlage nicht wiederhergestellt: ${(fehler as Error).message}`;
  }
}
