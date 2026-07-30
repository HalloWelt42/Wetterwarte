// Wetterdaten des aktiven Ortes - als Fassade ueber die geteilte Datenquellen-Schicht.
//
// Der Store abonniert fuer den aktiven Ort die Bereiche basis/warnungen/blitze/luft/pollen
// und spiegelt sie reaktiv in seine Scheiben. Weil jede Quelle fest an ihren Ort gebunden
// ist (siehe datenquelle.svelte.ts), kann ein Ortswechsel keine fremden Daten einspielen.
//
// Diese Fassade haelt bestehende Kacheln lauffaehig; kuenftig abonnieren einzelne Widgets
// die Datenquellen direkt - auch fuer einen eigenen, pro Kachel gewaehlten Ort.
import { schreib } from "./speicher";
import { abonniere, frischeZeitkritisch, gibFrei } from "./datenquelle.svelte";
import type { Aktuell, Blitze, Luft, Nowcast, Pollen, Stunde, Tag, Warnung } from "./typen";

interface Basis {
  ort: { name: string; region: string };
  aktuell: Aktuell;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string };
  nowcast: Nowcast | null;
}

export const wetter = $state<{
  slug: string;
  ort: string;
  aktuell: Aktuell | null;
  stunden: Stunde[];
  tage: Tag[];
  sonne: { aufgang: string; untergang: string } | null;
  warnungen: Warnung[];
  luft: Luft | null;
  nowcast: Nowcast | null;
  blitze: Blitze | null;
  pollen: Pollen | null;
  geladen: boolean;
  aktualisiert: number;
}>({
  slug: "",
  ort: "",
  aktuell: null,
  stunden: [],
  tage: [],
  sonne: null,
  warnungen: [],
  luft: null,
  nowcast: null,
  blitze: null,
  pollen: null,
  geladen: false,
  aktualisiert: 0,
});

const BEREICHE = ["basis", "warnungen", "blitze", "luft", "pollen"] as const;

let loesen: (() => void) | null = null;

function verbindeQuellen(slug: string): void {
  loesen?.(); // Verbindung zum vorigen Ort loesen (Abos freigeben, Spiegel-Effekte stoppen)

  const basis = abonniere("basis", slug);
  const warnungen = abonniere("warnungen", slug);
  const blitze = abonniere("blitze", slug);
  const luft = abonniere("luft", slug);
  const pollen = abonniere("pollen", slug);

  const stop = $effect.root(() => {
    $effect(() => {
      const d = basis.data as Basis | null;
      if (!d) return;
      wetter.ort = d.ort.name;
      wetter.aktuell = d.aktuell;
      wetter.stunden = d.stunden;
      wetter.tage = d.tage;
      wetter.sonne = d.sonne;
      wetter.nowcast = d.nowcast ?? null;
      wetter.geladen = true;
      wetter.aktualisiert = basis.aktualisiert;
    });
    $effect(() => {
      wetter.warnungen = (warnungen.data as Warnung[] | null) ?? [];
    });
    $effect(() => {
      wetter.blitze = (blitze.data as Blitze | null) ?? null;
    });
    $effect(() => {
      wetter.luft = (luft.data as Luft | null) ?? null;
    });
    $effect(() => {
      wetter.pollen = (pollen.data as Pollen | null) ?? null;
    });
  });

  loesen = () => {
    stop();
    for (const b of BEREICHE) gibFrei(b, slug);
  };
}

// Beim Zurueckkehren zum Tab die zeitkritischen Bereiche sofort auffrischen.
if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) frischeZeitkritisch();
  });
}

export async function ladeWetter(slug: string): Promise<void> {
  wetter.slug = slug;
  schreib("ort.aktiv", slug); // zuletzt betrachteten Ort merken
  verbindeQuellen(slug);
}
