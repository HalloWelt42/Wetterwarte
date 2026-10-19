// Was jede Telefon-Kachel bekommt: ihre Lage im Raster (w, h wählen die Form), ihre Einstellungen,
// die Daten des Orts und die Zeitzone des Orts.
import type { TelefonKachel } from "../kern/gemeinsam";
import type { Kompakt } from "./typen";

export interface KachelProps {
  kachel: TelefonKachel;
  daten: Kompakt;
  zone: string;
}

/** Form einer Kachel als "WxH", etwa "2x1". */
export function form(k: TelefonKachel): string {
  return `${k.w}x${k.h}`;
}
