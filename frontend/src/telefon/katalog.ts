// Telefon-Kacheltypen in der Oberfläche: Komponente, Detailblatt, benötigte Datenbereiche.
// Titel, Größen und Einstellungen stehen im gemeinsamen Katalog (gemeinsam/telefon-katalog.json);
// hier nur, was die Oberfläche zusätzlich braucht. Jeder Typ des Katalogs hat genau einen Eintrag.
import type { Component } from "svelte";
import { telefonKatalog } from "../kern/gemeinsam";
import JetztKachel from "./kacheln/Jetzt.svelte";
import JetztBlatt from "./blaetter/Jetzt.svelte";
import MesswertKachel from "./kacheln/Messwert.svelte";
import MesswertBlatt from "./blaetter/Messwert.svelte";
import HeuteKachel from "./kacheln/Heute.svelte";
import HeuteBlatt from "./blaetter/Heute.svelte";
import StundenKachel from "./kacheln/Stunden.svelte";
import StundenBlatt from "./blaetter/Stunden.svelte";
import TageKachel from "./kacheln/Tage.svelte";
import TageBlatt from "./blaetter/Tage.svelte";
import RegenKachel from "./kacheln/Regen.svelte";
import RegenBlatt from "./blaetter/Regen.svelte";
import WindKachel from "./kacheln/Wind.svelte";
import WindBlatt from "./blaetter/Wind.svelte";
import UvKachel from "./kacheln/Uv.svelte";
import UvBlatt from "./blaetter/Uv.svelte";
import LuftKachel from "./kacheln/Luft.svelte";
import LuftBlatt from "./blaetter/Luft.svelte";
import PollenKachel from "./kacheln/Pollen.svelte";
import PollenBlatt from "./blaetter/Pollen.svelte";
import SonneKachel from "./kacheln/Sonne.svelte";
import SonneBlatt from "./blaetter/Sonne.svelte";
import MondKachel from "./kacheln/Mond.svelte";
import MondBlatt from "./blaetter/Mond.svelte";
import WarnungenKachel from "./kacheln/Warnungen.svelte";
import WarnungenBlatt from "./blaetter/Warnungen.svelte";
import BlitzeKachel from "./kacheln/Blitze.svelte";
import BlitzeBlatt from "./blaetter/Blitze.svelte";
import RadarKachel from "./kacheln/Radar.svelte";
import MonatKachel from "./kacheln/Monat.svelte";
import MonatBlatt from "./blaetter/Monat.svelte";

export type BereichName = "basis" | "warnungen" | "blitze" | "luft" | "pollen";

export interface TelefonTyp {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  komponente: Component<any>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  detail: Component<any> | null;
  bereiche: BereichName[];
  fehltHinweis?: string;
  ziel?: "karte"; // Tippen öffnet einen Reiter statt eines Detailblatts
}

export const telefonTypen: Record<string, TelefonTyp> = {
  jetzt: { komponente: JetztKachel, detail: JetztBlatt, bereiche: ["basis"] },
  messwert: { komponente: MesswertKachel, detail: MesswertBlatt, bereiche: ["basis"] },
  heute: { komponente: HeuteKachel, detail: HeuteBlatt, bereiche: ["basis"] },
  stunden: { komponente: StundenKachel, detail: StundenBlatt, bereiche: ["basis"] },
  tage: { komponente: TageKachel, detail: TageBlatt, bereiche: ["basis"] },
  regen: { komponente: RegenKachel, detail: RegenBlatt, bereiche: ["basis"] },
  wind: { komponente: WindKachel, detail: WindBlatt, bereiche: ["basis"] },
  uv: { komponente: UvKachel, detail: UvBlatt, bereiche: ["basis"] },
  luft: { komponente: LuftKachel, detail: LuftBlatt, bereiche: ["luft"] },
  pollen: { komponente: PollenKachel, detail: PollenBlatt, bereiche: ["pollen"] },
  sonne: { komponente: SonneKachel, detail: SonneBlatt, bereiche: ["basis"] },
  mond: { komponente: MondKachel, detail: MondBlatt, bereiche: [] },
  warnungen: { komponente: WarnungenKachel, detail: WarnungenBlatt, bereiche: ["warnungen"], fehltHinweis: "Warnlage unbekannt" },
  blitze: { komponente: BlitzeKachel, detail: BlitzeBlatt, bereiche: ["blitze"] },
  radar: { komponente: RadarKachel, detail: null, bereiche: [], ziel: "karte" },
  monat: { komponente: MonatKachel, detail: MonatBlatt, bereiche: [] },
};

// Wache: jeder Katalogtyp braucht hier einen Eintrag (fällt in der Entwicklung sofort auf).
for (const typ of Object.keys(telefonKatalog.typen)) {
  if (!telefonTypen[typ]) console.error(`Telefon-Kacheltyp ohne Komponente: ${typ}`);
}
