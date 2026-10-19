// Rasterlogik des Telefon-Editors (3 Spalten): Kacheln verschieben, Größe ändern, hinzufügen.
// Regel wie auf einem Startbildschirm: Die bewegte Kachel bekommt ihren Platz, was im Weg ist,
// weicht nach unten aus, die Reihenfolge bleibt; nur ganz leere Reihen fallen weg. Ergebnis ohne
// Überlappung und innerhalb der 3 Spalten, wie das Backend es prüft. Reine Funktionen.
import type { TelefonKachel } from "../../kern/gemeinsam";

export const SPALTEN = 3;

function ueberlappt(a: TelefonKachel, b: { x: number; y: number; w: number; h: number }): boolean {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

function passt(gesetzt: TelefonKachel[], k: { x: number; y: number; w: number; h: number }): boolean {
  return k.x >= 0 && k.x + k.w <= SPALTEN && k.y >= 0 && !gesetzt.some((g) => ueberlappt(g, k));
}

/** Überlappungen auflösen: `fest` behält seine Lage, die übrigen behalten ihre Reihe, wenn sie
 *  frei ist, sonst weichen sie nach unten aus (in Lesereihenfolge). Danach fallen leere Reihen weg. */
export function verdichte(kacheln: TelefonKachel[], fest?: string): TelefonKachel[] {
  const gesetzt: TelefonKachel[] = [];
  const f = kacheln.find((k) => k.id === fest);
  if (f) gesetzt.push({ ...f, x: Math.min(Math.max(0, f.x), SPALTEN - f.w), y: Math.max(0, f.y) });
  const rest = kacheln.filter((k) => k.id !== fest).sort((a, b) => a.y - b.y || a.x - b.x);
  for (const k of rest) {
    const x = Math.min(Math.max(0, k.x), SPALTEN - k.w);
    let y = Math.max(0, k.y);
    while (!passt(gesetzt, { x, y, w: k.w, h: k.h })) y += 1;
    gesetzt.push({ ...k, x, y });
  }
  return ohneLeereReihen(gesetzt).sort((a, b) => a.y - b.y || a.x - b.x);
}

/** Reihen, in denen keine Kachel liegt, entfernen (alles darunter rückt um diese Reihen hoch). */
function ohneLeereReihen(kacheln: TelefonKachel[]): TelefonKachel[] {
  const belegt = new Set<number>();
  for (const k of kacheln) for (let r = k.y; r < k.y + k.h; r++) belegt.add(r);
  const ende = Math.max(0, ...kacheln.map((k) => k.y + k.h));
  const neu: number[] = [];
  let zaehler = 0;
  for (let r = 0; r < ende; r++) {
    neu[r] = zaehler;
    if (belegt.has(r)) zaehler += 1;
  }
  return kacheln.map((k) => ({ ...k, y: neu[k.y] ?? k.y }));
}

/** Erste freie Lage für eine neue Kachel (von oben links). */
export function freieLage(kacheln: TelefonKachel[], w: number, h: number): { x: number; y: number } {
  for (let y = 0; ; y += 1) {
    for (let x = 0; x + w <= SPALTEN; x += 1) {
      if (passt(kacheln, { x, y, w, h })) return { x, y };
    }
  }
}

/** Kachel an eine Zielzelle verschieben, die anderen rücken. */
export function verschiebe(kacheln: TelefonKachel[], id: string, x: number, y: number): TelefonKachel[] {
  return verdichte(
    kacheln.map((k) => (k.id === id ? { ...k, x, y } : k)),
    id,
  );
}

/** Größe ändern; ragt die Kachel rechts hinaus, rückt sie nach links. */
export function groesse(kacheln: TelefonKachel[], id: string, w: number, h: number): TelefonKachel[] {
  return verdichte(
    kacheln.map((k) => (k.id === id ? { ...k, w, h, x: Math.min(k.x, SPALTEN - w) } : k)),
    id,
  );
}

export function reihenVon(kacheln: TelefonKachel[]): number {
  return Math.max(0, ...kacheln.map((k) => k.y + k.h));
}
