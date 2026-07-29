// Typen fuer die (vorerst platzhalterhaften) Wetterdaten des Dashboards.

export type TempKlasse =
  | "t-frost"
  | "t-kalt"
  | "t-kuehl"
  | "t-mild"
  | "t-warm"
  | "t-heiss"
  | "t-extrem";

export interface OrtEintrag {
  slug: string;
  name: string;
  region: string;
  icon: string;
  temp: number;
  aktiv?: boolean;
}

export interface Aktuell {
  temperatur: number;
  tempKlasse: TempKlasse;
  gefuehlt: number;
  tageshoch: number;
  zustandText: string;
  icon: string;
  feuchte: number;
  wind: number;
  windRichtung: string;
  windGrad?: number;
  druck: number;
  sicht: number;
  taupunkt: number;
  bewoelkung: number;
  uv?: number;
}

export interface Stunde {
  zeit: string;
  icon: string;
  temp: number;
  tempKlasse: TempKlasse;
  regen?: number;
}

export interface Tag {
  kurz: string;
  icon: string;
  hi: number;
  lo: number;
  bandLinks: number;
  bandRechts: number;
}

export interface Warnung {
  stufe: 1 | 2 | 3 | 4;
  titel: string;
  zeit: string;
  icon?: string;
  faIcon?: string;
}
