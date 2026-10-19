// Antwort von /wetter/kompakt/{ort} (backend schemas/kompakt.py). Zahlen ungerundet, Zeiten ISO mit Versatz.

export type Status = "ok" | "alt" | "fehlt";

export interface Bereich {
  status: Status;
  stand: string | null;
}

export interface Jetzt {
  zeit: string;
  temp: number;
  gefuehlt: number;
  code: number;
  tag: boolean;
  feuchte: number;
  taupunkt: number;
  druck: number;
  druck_tendenz: number | null;
  sicht_km: number | null;
  bewoelkung: number;
  wind: number;
  boeen: number;
  wind_grad: number;
  uv: number;
  regen_mm: number;
}

export interface Stunde {
  zeit: string;
  temp: number;
  gefuehlt: number;
  code: number;
  tag: boolean;
  regen_wahrsch: number | null;
  regen_mm: number;
  wind: number;
  boeen: number;
  wind_grad: number;
  uv: number;
  feuchte: number;
  taupunkt: number;
  druck: number;
  sicht_km: number | null;
  bewoelkung: number;
}

export interface Tag {
  datum: string;
  code: number;
  hoch: number;
  tief: number;
  regen_wahrsch: number | null;
  regen_mm: number;
  wind_max: number;
  boeen_max: number;
  uv_max: number;
  uv_max_zeit: string | null; // Stunde des Höchstwerts (Ortszeit als ISO), soweit bekannt
  sonnenaufgang: string | null;
  sonnenuntergang: string | null;
  tageslaenge_s: number;
}

export interface Regen {
  schritt_min: number;
  werte: number[];
  beginn_min: number | null;
  ende_min: number | null;
  max_mm_h: number;
  quelle: "modell" | "radar";
}

export interface Warnung {
  stufe: number;
  ereignis: string;
  ueberschrift: string;
  beschreibung: string;
  von: string | null;
  bis: string | null;
}

export interface Blitze {
  anzahl_30: number;
  anzahl_60: number;
  naechster_km: number | null;
  naechster_grad: number | null;
  zuletzt: string | null;
  einschlaege: { km: number; grad: number; zeit: string }[];
}

export interface Luft {
  index: number;
  stufe: string;
  schadstoffe: { schluessel: string; titel: string; wert: number; einheit: string }[];
}

export interface Pollenart {
  schluessel: string;
  titel: string;
  heute: number;
  morgen: number;
  uebermorgen: number;
}

/** Ein kommendes oder laufendes Wetterereignis (backend schemas/lage.py, docs/WARNUNGEN.md). */
export interface Ereignis {
  art: import("../kern/gemeinsam").Meldeart;
  schluessel: string;
  klasse: string;
  rang: number;
  stufe: number;
  beginn: string | null;
  laeuft: boolean;
  vorlauf_min: number | null;
  vorlaufstufe: number | null;
  quelle: "radar" | "vorhersage" | "amtlich" | "blitze";
  titel: string;
  text: string;
  bausteine: string[];
}

export interface Kompakt {
  ort: { slug: string; name: string; region: string; lat: number; lon: number; zeitzone: string };
  zeit: string;
  bereiche: Record<"basis" | "warnungen" | "blitze" | "luft" | "pollen", Bereich> & { nowcast?: Bereich };
  jetzt: Jetzt | null;
  stunden: Stunde[];
  jetzt_index: number;
  tage: Tag[];
  regen: Regen | null;
  warnungen: Warnung[] | null;
  blitze: Blitze | null;
  luft: Luft | null;
  pollen: { region: string; arten: Pollenart[] } | null;
  lage?: Ereignis[]; // fehlt im gemerkten Stand älterer Fassungen
}
