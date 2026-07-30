// Pro-Widget-Datenfassade: liefert die Wetter-Scheiben fuer EINEN Ort, indem sie die
// passenden Datenquellen abonniert. Jedes Widget ruft das mit seinem eigenen Ort auf -
// dank Dedup in datenquelle.svelte.ts teilen sich Kacheln desselben Ortes die Abrufe.
//
// Als Funktion mit $effect: nur waehrend der Komponenten-Initialisierung aufrufen
// (dann haengt das Abo am Lebenszyklus der Kachel und wird beim Entfernen geloest).
import { abonniere, gibFrei } from "./datenquelle.svelte";
import type { Aktuell, Blitze, Luft, Nowcast, Pollen, Stunde, Tag, Warnung } from "./typen";

interface Basis {
  ort: { name: string; region: string };
  aktuell: Aktuell;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string };
  nowcast: Nowcast | null;
}

const BEREICHE = ["basis", "warnungen", "blitze", "luft", "pollen"] as const;

export interface OrtDaten {
  readonly basis: Basis | null;
  readonly warnungen: Warnung[] | null;
  readonly blitze: Blitze | null;
  readonly luft: Luft | null;
  readonly pollen: Pollen | null;
  readonly geladen: boolean;
}

export function nutzeOrtDaten(ort: () => string): OrtDaten {
  let quellen = $state<Record<string, { data: unknown }>>({});

  $effect(() => {
    const o = ort();
    if (!o) {
      quellen = {};
      return;
    }
    quellen = {
      basis: abonniere("basis", o),
      warnungen: abonniere("warnungen", o),
      blitze: abonniere("blitze", o),
      luft: abonniere("luft", o),
      pollen: abonniere("pollen", o),
    };
    return () => {
      for (const b of BEREICHE) gibFrei(b, o);
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
  };
}
