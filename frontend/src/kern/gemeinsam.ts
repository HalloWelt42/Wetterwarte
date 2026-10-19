// Mit dem Backend geteilte Dateien (gemeinsam/ im Projektwurzelverzeichnis), beim Bau eingebaut.
// Einzige Wahrheit über Telefon-Kacheltypen und Wettercodes; das Backend liest dieselben Dateien.

export interface Option {
  wert: string;
  titel: string;
}

export interface Einstellung {
  schluessel: string;
  titel: string;
  art: "auswahl" | "mehrfach";
  standard: string | string[];
  optionen: Option[];
}

export interface TelefonTypDef {
  titel: string;
  familie: string;
  symbol: string; // Font-Awesome-Klasse
  beschreibung: string;
  groessen: string[]; // "WxH"
  seiten: string[]; // auf welche Telefon-Seiten der Typ darf
  einstellungen: Einstellung[];
}

export interface TelefonKachel {
  id: string;
  typ: string;
  x: number;
  y: number;
  w: number;
  h: number;
  conf: Record<string, unknown>;
}

export interface TelefonSeite {
  schluessel: string;
  titel: string;
  symbol: string;
}

export interface TelefonKatalog {
  spalten: number;
  seiten: TelefonSeite[];
  familien: { schluessel: string; titel: string }[];
  typen: Record<string, TelefonTypDef>;
  vorlage: Record<string, Omit<TelefonKachel, "id">[]>;
  // Vorlagen je Profilname (Seiten, die abweichen); das Backend wendet sie beim Anlegen an.
  profilvorlagen?: Record<string, Record<string, Omit<TelefonKachel, "id">[]> | string>;
}

/** Telefon-Layout eines Profils: Kacheln je Seite. */
export interface TelefonLayout {
  seiten: Record<string, TelefonKachel[]>;
}

export interface Wettercodes {
  gruppen: { codes: number[]; tag: string; nacht: string; text: string }[];
  sonst: { tag: string; nacht: string; text: string };
}

/** Aktive Warnungen (gemeinsam/meldungen.json): was die Oberfläche davon braucht. */
export type Meldeart = "warnung" | "niederschlag" | "gewitter" | "wind";

export interface Meldeoption {
  wert: number;
  name: string;
}

export interface Meldekatalog {
  arten: { schluessel: Meldeart; name: string; symbol: string; beschreibung: string; vorlaufstufen?: number[] }[];
  optionen: {
    vorlauf_min: Meldeoption[];
    niederschlag_ab: Meldeoption[];
    wind_ab: Meldeoption[];
    vorgabe: {
      arten: Meldeart[];
      vorlauf_min: number;
      niederschlag_ab: number;
      wind_ab: number;
      nachtruhe: { an: boolean; von: number; bis: number; ab_stufe: number };
    };
  };
  ansagen: { pause_ms: number; saetze: Record<string, string> };
}

export const telefonKatalog: TelefonKatalog = __TELEFON_KATALOG__;
export const meldekatalog: Meldekatalog = __MELDUNGEN__;
export const wettercodes: Wettercodes = __WETTERCODES__;

/** Wert einer Kachel-Einstellung oder ihr Standard aus dem Katalog. */
export function einstellung<T = string>(typ: string, conf: Record<string, unknown>, schluessel: string): T {
  if (conf[schluessel] !== undefined) return conf[schluessel] as T;
  return telefonKatalog.typen[typ]?.einstellungen.find((e) => e.schluessel === schluessel)?.standard as T;
}
