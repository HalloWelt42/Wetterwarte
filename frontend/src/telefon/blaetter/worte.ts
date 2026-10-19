// Einordnung von Messwerten in kurze Worte für die Detailblätter (nur Deutung echter Werte,
// nie Ersatzwerte). Grenzen nach den üblichen Faustregeln.
import { beaufort, zahl } from "../format";

/** Warum sich die Temperatur anders anfühlt. */
export function gefuehltSatz(temp: number, gefuehlt: number, wind: number): string {
  const d = gefuehlt - temp;
  if (d <= -1) return wind >= 10 ? "Wind kühlt" : "fühlt sich kühler an";
  if (d >= 1) return "Feuchte macht es wärmer";
  return "wie gemessen";
}

export function feuchteWort(prozent: number): string {
  if (prozent < 30) return "sehr trocken";
  if (prozent < 45) return "trocken";
  if (prozent < 70) return "angenehm";
  if (prozent < 90) return "feucht";
  return "sehr feucht";
}

export function taupunktWort(taupunkt: number): string {
  if (taupunkt < 10) return "trockene Luft";
  if (taupunkt < 16) return "angenehm";
  if (taupunkt < 19) return "leicht schwül";
  if (taupunkt < 22) return "schwül";
  return "drückend schwül";
}

// Sicht und Bewölkung mit denselben Grenzen und Worten wie die Messwert-Kachel (kacheln/messwerte.ts)
export function sichtWort(km: number): string {
  if (km < 1) return "Nebel";
  if (km < 5) return "dunstig";
  if (km < 10) return "mäßige Sicht";
  return "gute Sicht";
}

/** Bewölkung nach Achteln (0 wolkenlos, 1 bis 2 heiter, 3 bis 5 wolkig, 6 bis 7 stark bewölkt, 8 bedeckt). */
export function bewoelkungWort(prozent: number): string {
  const achtel = Math.round((prozent / 100) * 8);
  if (achtel === 0) return "wolkenlos";
  if (achtel <= 2) return "heiter";
  if (achtel <= 5) return "wolkig";
  if (achtel <= 7) return "stark bewölkt";
  return "bedeckt";
}

/** Regenstärke zu mm je Stunde. */
export function regenStaerke(mmH: number): string {
  if (mmH < 0.5) return "sehr leichter Regen";
  if (mmH < 2.5) return "leichter Regen";
  if (mmH < 10) return "mäßiger Regen";
  if (mmH < 50) return "starker Regen";
  return "sehr starker Regen";
}

/** Was man bei einer Beaufort-Stufe draußen sieht. */
const BEAUFORT_ZEICHEN = [
  "Rauch steigt senkrecht auf",
  "Rauch zeigt den Wind, Fahnen hängen still",
  "Wind im Gesicht spürbar, Blätter säuseln",
  "Blätter und dünne Zweige bewegen sich",
  "Zweige bewegen sich, loses Papier fliegt",
  "Kleine Bäume schwanken",
  "Starke Äste bewegen sich, Schirme schwer zu halten",
  "Ganze Bäume bewegen sich, Gehen wird mühsam",
  "Zweige brechen ab, Gehen erheblich erschwert",
  "Äste brechen, Dachziegel können herabfallen",
  "Bäume werden entwurzelt, Schäden an Häusern",
  "Schwere Sturmschäden",
  "Verwüstungen",
];

export function beaufortZeichen(kmh: number): string {
  return BEAUFORT_ZEICHEN[beaufort(kmh)];
}

/** UV-Index mit einer Nachkommastelle, 0 ohne. */
export function uvZahl(uv: number): string {
  return zahl(uv, uv > 0 && uv < 10 ? 1 : 0);
}

/** Rat zum UV-Index. */
export function uvRat(uv: number): string {
  if (uv < 3) return "Kein Schutz nötig.";
  if (uv < 6) return "Mittags Schatten suchen, Sonnencreme.";
  if (uv < 8) return "Hut, Sonnenbrille und Sonnencreme.";
  if (uv < 11) return "Mittags möglichst drinnen bleiben.";
  return "Sonne meiden.";
}
