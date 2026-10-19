// Pro-Widget-Datenfassade: liefert die Wetter-Scheiben fuer EINEN Ort, indem sie die
// passenden Datenquellen abonniert. Jedes Widget ruft das mit seinem eigenen Ort auf -
// dank Dedup in datenquelle.svelte.ts teilen sich Kacheln desselben Ortes die Abrufe.
//
// Als Funktion mit $effect: nur waehrend der Komponenten-Initialisierung aufrufen
// (dann haengt das Abo am Lebenszyklus der Kachel und wird beim Entfernen geloest).
import { abonniere, gibFrei, type Quelle, type Zustand } from "../kern/datenquelle.svelte";
import type { Aktuell, Blitze, Luft, Nowcast, Pollen, Stunde, Tag, Warnung } from "./typen";

interface Basis {
  ort: { name: string; region: string };
  aktuell: Aktuell;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string };
  nowcast: Nowcast | null;
}

export const BEREICHE = ["basis", "warnungen", "blitze", "luft", "pollen"] as const;
export type BereichName = (typeof BEREICHE)[number];

export interface OrtDaten {
  readonly basis: Basis | null;
  readonly warnungen: Warnung[] | null;
  readonly blitze: Blitze | null;
  readonly luft: Luft | null;
  readonly pollen: Pollen | null;
  readonly geladen: boolean;
  /** Zustand eines Bereichs (laedt, ok, alt, fehlt); nicht abonnierte gelten als ok. */
  zustand(bereich: BereichName): Zustand;
  /** Zeitpunkt der Daten eines Bereichs (ISO) oder null. */
  stand(bereich: BereichName): string | null;
}

/** Daten eines Orts für eine Kachel. `bereiche` nennt, was die Kachel braucht (aus dem Katalog);
 *  nur diese werden abonniert. */
export function nutzeOrtDaten(ort: () => string, bereiche: readonly BereichName[] = BEREICHE): OrtDaten {
  let quellen = $state<Partial<Record<BereichName, Quelle>>>({});

  $effect(() => {
    const o = ort();
    if (!o) {
      quellen = {};
      return;
    }
    const neu: Partial<Record<BereichName, Quelle>> = {};
    for (const b of bereiche) neu[b] = abonniere(b, o);
    quellen = neu;
    return () => {
      for (const b of bereiche) gibFrei(b, o);
    };
  });

  return {
    get basis() {
      return (quellen.basis?.data ?? null) as Basis | null;
    },
    get warnungen() {
      return (quellen.warnungen?.data ?? null) as Warnung[] | null;
    },
    get blitze() {
      return (quellen.blitze?.data ?? null) as Blitze | null;
    },
    get luft() {
      return (quellen.luft?.data ?? null) as Luft | null;
    },
    get pollen() {
      return (quellen.pollen?.data ?? null) as Pollen | null;
    },
    get geladen() {
      return quellen.basis?.data != null;
    },
    zustand(bereich: BereichName): Zustand {
      const q = quellen[bereich];
      return q ? q.zustand : bereiche.includes(bereich) ? "laedt" : "ok";
    },
    stand(bereich: BereichName): string | null {
      return quellen[bereich]?.stand ?? null;
    },
  };
}
