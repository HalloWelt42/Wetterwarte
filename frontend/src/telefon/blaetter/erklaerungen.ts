// Kurze Erklärtexte für Fachbegriffe in den Detailblättern. Wo kern/begriffe.ts schon einen Text
// hat, gilt dieser (eine Wahrheit für Desktop und Telefon); hier nur, was dort fehlt.
import { begriffe } from "../../kern/begriffe";

export interface Begriff {
  titel: string;
  text: string;
}

export const erklaerung = {
  gefuehlt: {
    titel: "Gefühlte Temperatur",
    text: "So warm oder kalt fühlt es sich draußen an. Wind kühlt zusätzlich, feuchte Wärme wirkt wärmer, als das Thermometer zeigt.",
  },
  taupunkt: { titel: "Taupunkt", text: begriffe.taupunkt },
  feuchte: {
    titel: "Relative Feuchte",
    text: "Wie viel Wasserdampf die Luft enthält, gemessen an dem, was sie bei dieser Temperatur höchstens halten kann. Bei 100 % bildet sich Nebel oder Tau.",
  },
  luftdruck: {
    titel: "Luftdruck",
    text: `${begriffe.hpa} Steigt er, wird es meist ruhiger; fällt er rasch, kommen oft Wind und Regen.`,
  },
  sicht: { titel: "Sicht", text: "Wie weit man waagerecht sehen kann. Unter 1 km spricht man von Nebel." },
  bewoelkung: { titel: "Bewölkung", text: "Welcher Anteil des Himmels von Wolken bedeckt ist: 0 % ist wolkenlos, 100 % ganz bedeckt." },
  boeen: { titel: "Böen", text: begriffe.boeen },
  beaufort: {
    titel: "Beaufort",
    text: "Windstärke in 13 Stufen von 0 (Windstille) bis 12 (Orkan), benannt nach dem, was man draußen sieht. Ab Stufe 9 spricht man von Sturm.",
  },
  uv: { titel: "UV-Index", text: begriffe.uv },
  luftindex: { titel: "Luftqualitätsindex", text: begriffe.aqi },
  feinstaub: { titel: "Feinstaub", text: `${begriffe.pm25} ${begriffe.pm10}` },
  ozon: { titel: "Ozon", text: begriffe.ozon },
  stickstoffdioxid: { titel: "Stickstoffdioxid", text: begriffe.no2 },
  pollenstufen: {
    titel: "Pollenflug-Stufen",
    text: "Keine, gering, mittel, hoch: wie viele Pollen einer Art in der Luft erwartet werden. Ein Punkt heißt gering, zwei mittel, drei hoch; dazwischen gibt es halbe Stufen wie gering bis mittel.",
  },
  regenMenge: {
    titel: "Regen in % und mm",
    text: "Die Prozentzahl sagt, wie wahrscheinlich es in dieser Stunde regnet. Die Millimeter sagen, wie viel: 1 mm ist 1 Liter auf den Quadratmeter.",
  },
  kurzfrist: {
    titel: "Kurzfristvorhersage",
    text: `${begriffe.nowcast} Das Wettermodell rechnet die nächsten 2 Stunden in Viertelstunden, danach gilt die Stundenvorhersage.`,
  },
  tagesband: {
    titel: "Was zeigt der Balken?",
    text: "Die Spanne von Tief bis Hoch des Tages, gemessen an der ganzen Woche. Der Punkt bei heute ist die Temperatur jetzt.",
  },
  daemmerung: {
    titel: "Dämmerung",
    text: "Nach Sonnenuntergang bleibt es noch eine Weile hell genug, um draußen ohne Licht zu lesen. Gezeigt ist das Ende dieser bürgerlichen Dämmerung.",
  },
  goldeneStunde: { titel: "Goldene Stunde", text: "Die Zeit vor Sonnenuntergang, in der die Sonne tief steht und warmes, weiches Licht gibt." },
  mondAnteil: {
    titel: "Beleuchteter Anteil",
    text: "So viel der sichtbaren Mondscheibe ist von der Sonne beleuchtet. Zunehmend heißt: Der helle Teil wächst bis zum Vollmond.",
  },
  warnstufen: {
    titel: "Warnstufen",
    text: "Amtliche Warnungen haben vier Stufen: 1 Wetterwarnung, 2 markante Wetterwarnung, 3 Unwetterwarnung, 4 Warnung vor extremem Unwetter.",
  },
  blitzUmkreis: {
    titel: "Umkreis und Messgebiet",
    text: "Die Ringe zeigen den in der Kachel eingestellten Umkreis. Die Zahlen für 30 und 60 Minuten zählen alle Einschläge im ganzen Messgebiet um den Ort.",
  },
} satisfies Record<string, Begriff>;

/** Erklärung zum Klimamittel mit dem tatsächlichen Zeitraum der Vergleichsjahre. */
export function klimamittel(von: number, bis: number): Begriff {
  return {
    titel: `Klimamittel ${von} bis ${bis}`,
    text: `Der Durchschnitt der Jahre ${von} bis ${bis} für denselben Monat. Plus heißt wärmer als dieser Durchschnitt, Minus kühler.`,
  };
}
