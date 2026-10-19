// Stundenliste der Blätter (Stunden, Regen): Stunden nach Kalendertagen des Orts gruppiert, mit
// Sonnenauf- und -untergang als eigenen Einträgen zwischen den Stunden.
import type { Kompakt, Stunde } from "../typen";
import { kalendertag, tagLang, tagNah, gross } from "./datum";

export type Eintrag = { art: "stunde"; stunde: Stunde; jetzt: boolean } | { art: "sonne"; zeit: string; aufgang: boolean };

export interface Tagesgruppe {
  datum: string;
  titel: string;
  stunden: number;
  eintraege: Eintrag[];
}

/** Stunden d.stunden[von, bis) mit den Sonnenereignissen dazwischen, nach Tagen gruppiert. */
export function stundenNachTagen(d: Kompakt, zone: string, von: number, bis: number, jetzt: Date): Tagesgruppe[] {
  const stunden = d.stunden.slice(Math.max(0, von), Math.max(0, bis));
  if (!stunden.length) return [];
  const anfang = Math.max(jetzt.getTime(), new Date(stunden[0].zeit).getTime());
  const ende = new Date(stunden[stunden.length - 1].zeit).getTime() + 3_600_000;

  const sonne: { t: number; e: Eintrag }[] = d.tage.flatMap((t) =>
    [
      [t.sonnenaufgang, true],
      [t.sonnenuntergang, false],
    ]
      .filter((p): p is [string, boolean] => !!p[0])
      .map(([zeit, aufgang]) => ({ t: new Date(zeit).getTime(), e: { art: "sonne", zeit, aufgang } as Eintrag }))
      .filter(({ t: ms }) => ms > anfang && ms < ende),
  );
  const alle = [
    ...stunden.map((s, i) => ({ t: new Date(s.zeit).getTime(), e: { art: "stunde", stunde: s, jetzt: von + i === d.jetzt_index } as Eintrag })),
    ...sonne,
  ].sort((a, b) => a.t - b.t || (a.e.art === "stunde" ? -1 : 1));

  const heute = kalendertag(jetzt, zone);
  const gruppen: Tagesgruppe[] = [];
  for (const { e } of alle) {
    const datum = kalendertag(e.art === "stunde" ? e.stunde.zeit : e.zeit, zone);
    let g = gruppen[gruppen.length - 1];
    if (!g || g.datum !== datum) {
      const nah = tagNah(datum, heute);
      g = { datum, titel: nah === tagLang(datum) ? nah : `${gross(nah)}, ${tagLang(datum)}`, stunden: 0, eintraege: [] };
      gruppen.push(g);
    }
    g.eintraege.push(e);
    if (e.art === "stunde") g.stunden += 1;
  }
  return gruppen;
}
