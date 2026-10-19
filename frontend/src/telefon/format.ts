// Zahlen und Begriffe für die Telefonansicht: deutsches Komma, kurze Texte.

export function zahl(v: number, stellen = 0): string {
  return v.toLocaleString("de-DE", { minimumFractionDigits: stellen, maximumFractionDigits: stellen, useGrouping: false });
}

export function grad(v: number): string {
  return `${Math.round(v)}°`;
}

const RICHTUNGEN = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"];
const RICHTUNGEN_LANG = ["Nord", "Nordost", "Ost", "Südost", "Süd", "Südwest", "West", "Nordwest"];

/** Himmelsrichtung, aus der der Wind kommt (kurz). */
export function richtung(gradzahl: number): string {
  return RICHTUNGEN[Math.round(gradzahl / 45) % 8];
}

export function richtungLang(gradzahl: number): string {
  return RICHTUNGEN_LANG[Math.round(gradzahl / 45) % 8];
}

const BEAUFORT = [1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117];
const BEAUFORT_TEXT = [
  "Windstill", "Leiser Zug", "Leichte Brise", "Schwache Brise", "Mäßige Brise", "Frische Brise",
  "Starker Wind", "Steifer Wind", "Stürmischer Wind", "Sturm", "Schwerer Sturm", "Orkanartiger Sturm", "Orkan",
];

export function beaufort(kmh: number): number {
  const i = BEAUFORT.findIndex((g) => kmh < g);
  return i === -1 ? 12 : i;
}

export function windWort(kmh: number): string {
  return BEAUFORT_TEXT[beaufort(kmh)];
}

export function uvWort(uv: number): string {
  if (uv < 3) return "gering";
  if (uv < 6) return "mäßig";
  if (uv < 8) return "hoch";
  if (uv < 11) return "sehr hoch";
  return "extrem";
}

/** DWD-Pollenstufe 0 bis 3 (halbe Schritte) in Worten. */
export function pollenWort(stufe: number): string {
  if (stufe < 0) return "keine Angabe";
  if (stufe < 0.5) return "keine";
  if (stufe < 1) return "kaum";
  if (stufe < 1.5) return "gering";
  if (stufe < 2) return "gering bis mittel";
  if (stufe < 2.5) return "mittel";
  if (stufe < 3) return "mittel bis hoch";
  return "hoch";
}

/** Kurzes Wort für enge Kacheln (die Zwischenstufen in einem Wort). */
export function pollenWortKurz(stufe: number): string {
  if (stufe < 0) return "keine Angabe";
  if (stufe < 0.5) return "keine";
  if (stufe < 1) return "kaum";
  if (stufe < 1.5) return "gering";
  if (stufe < 2) return "mäßig";
  if (stufe < 2.5) return "mittel";
  if (stufe < 3) return "stark";
  return "hoch";
}

/** Anzahl Stufenpunkte (0 bis 3) zu einer DWD-Pollenstufe. */
export function pollenPunkte(stufe: number): number {
  return stufe < 0.5 ? 0 : Math.min(3, Math.ceil(stufe));
}

/** Luftgüte: CSS-Variable passend zur Stufe des europäischen Index. */
export function luftVar(index: number): string {
  if (index <= 40) return "--gut";
  if (index <= 60) return "--w1";
  if (index <= 80) return "--w2";
  if (index <= 100) return "--w3";
  return "--w4";
}

export function dauer(sekunden: number): string {
  const min = Math.round(sekunden / 60);
  return `${Math.floor(min / 60)} h ${String(min % 60).padStart(2, "0")}`;
}
