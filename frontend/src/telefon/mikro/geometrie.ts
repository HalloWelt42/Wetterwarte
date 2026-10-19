// Gemeinsame Geometrie der Mikrodiagramme (Vorlage: mockups/telefon/mikro.js).

/** Glatte Linie durch Punkte (monotone kubische Interpolation, kein Überschwingen). */
export function glattePfad(p: [number, number][]): string {
  const n = p.length;
  if (n < 2) return "";
  const d: number[] = [];
  const m: number[] = [];
  for (let i = 0; i < n - 1; i++) d.push((p[i + 1][1] - p[i][1]) / (p[i + 1][0] - p[i][0] || 1));
  m[0] = d[0];
  m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  let s = `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}`;
  for (let i = 0; i < n - 1; i++) {
    const h = (p[i + 1][0] - p[i][0]) / 3;
    s += ` C${(p[i][0] + h).toFixed(1)},${(p[i][1] + m[i] * h).toFixed(1)} ${(p[i + 1][0] - h).toFixed(1)},${(p[i + 1][1] - m[i + 1] * h).toFixed(1)} ${p[i + 1][0].toFixed(1)},${p[i + 1][1].toFixed(1)}`;
  }
  return s;
}

/** CSS-Variable der Temperaturstufe (gleiche Grenzen wie am Desktop). */
export function tempVar(t: number): string {
  if (t < 0) return "--t-frost";
  if (t < 8) return "--t-kalt";
  if (t < 14) return "--t-kuehl";
  if (t < 20) return "--t-mild";
  if (t < 26) return "--t-warm";
  if (t < 32) return "--t-heiss";
  return "--t-extrem";
}

/** Klasse der Temperaturstufe für Text (t-frost bis t-extrem). */
export function tempKlasse(t: number): string {
  return tempVar(t).slice(2);
}

let zaehler = 0;
/** Eindeutige ID für Verläufe und Masken im SVG. */
export function svgId(praefix: string): string {
  zaehler += 1;
  return `${praefix}-${zaehler}`;
}
