// Mondphase, rein rechnerisch über den synodischen Monat (unabhängig von der Zeitzone, weil sie auf
// absoluter Zeit beruht). Gemeinsam für Desktop und Telefon.

export const SYNODISCH = 29.530588853; // Tage von Neumond zu Neumond
const NEUMOND0 = Date.UTC(2000, 0, 6, 18, 14, 0);

export interface Mondstand {
  phase: number; // 0 Neumond, 0,5 Vollmond, gegen 1 wieder Neumond
  anteil: number; // beleuchteter Anteil 0 bis 1
  zunehmend: boolean;
  tageBisVoll: number;
  tageBisNeu: number;
  name: string; // Phase in Worten
  emoji: string;
}

const NAMEN: [number, string, string][] = [
  [0.025, "Neumond", "🌑"],
  [0.235, "zunehmende Sichel", "🌒"],
  [0.265, "erstes Viertel", "🌓"],
  [0.485, "zunehmender Mond", "🌔"],
  [0.515, "Vollmond", "🌕"],
  [0.735, "abnehmender Mond", "🌖"],
  [0.765, "letztes Viertel", "🌗"],
  [0.975, "abnehmende Sichel", "🌘"],
  [1.01, "Neumond", "🌑"],
];

export function mondstand(zeit: Date): Mondstand {
  const tage = (zeit.getTime() - NEUMOND0) / 86400000;
  const alter = ((tage % SYNODISCH) + SYNODISCH) % SYNODISCH;
  const phase = alter / SYNODISCH;
  const [, name, emoji] = NAMEN.find(([grenze]) => phase < grenze) ?? NAMEN[0];
  return {
    phase,
    anteil: (1 - Math.cos(phase * 2 * Math.PI)) / 2,
    zunehmend: phase < 0.5,
    tageBisVoll: ((0.5 - phase + 1) % 1) * SYNODISCH,
    tageBisNeu: ((1 - phase) % 1) * SYNODISCH,
    name,
    emoji,
  };
}
