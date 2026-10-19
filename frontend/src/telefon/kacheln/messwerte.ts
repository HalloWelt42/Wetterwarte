// Die Werte der Messwert-Kachel (Einstellung "groesse"): Titel, Symbol, Einheit, Verlauf und die
// kurze Zeile unter dem Wert. Titel und Auswahl stehen im Katalog; hier nur, was die Oberfläche
// zusätzlich braucht. Jeder Wert des Katalogs hat genau einen Eintrag.
import { DRUCK_STABIL_HPA } from "../../kern/grenzen";
import { telefonKatalog } from "../../kern/gemeinsam";
import { grad, richtungLang, zahl } from "../format";
import { tempKlasse } from "../mikro/geometrie";
import type { Kompakt, Stunde } from "../typen";

/** Zeile unter dem Wert: Text, optional mit einer fetten Zahl dahinter. */
export interface Zusatz {
  text: string;
  fett?: string;
}

export interface Messwert {
  art: string;
  titel: string; // aus dem Katalog
  kurz: string; // Titel in 1x1
  symbol: string;
  einheit: string; // klein hinter dem Wert
  einheitVerlauf: string; // an Tief und Hoch im Verlauf
  farbe: string; // Verlauf: CSS-Variable oder "temp"
  flaeche: boolean;
  saeulen: boolean; // Verlauf als Säulen (mm je Stunde) statt als Linie
  jetzt: (d: Kompakt) => number | null;
  stunde: (s: Stunde) => number | null;
  text: (v: number) => string;
  klasse: (v: number) => string;
  zusatz: (d: Kompakt, v: number, eng: boolean) => Zusatz; // eng: in 1x1 und 2x1
}

/** Sichtweite in Worten (Nebel unter 1 km, Dunst bis 5 km wie in der Wetterbeobachtung). */
function sichtWort(km: number): string {
  if (km < 1) return "Nebel";
  if (km < 5) return "dunstig";
  if (km < 10) return "mäßige Sicht";
  return "gute Sicht";
}

/** Bewölkung in Worten nach Achteln (0 wolkenlos, 1 bis 2 heiter, 3 bis 5 wolkig, 6 bis 7 stark bewölkt, 8 bedeckt). */
function wolkenWort(prozent: number): string {
  const achtel = Math.round((prozent / 100) * 8);
  if (achtel === 0) return "wolkenlos";
  if (achtel <= 2) return "heiter";
  if (achtel <= 5) return "wolkig";
  if (achtel <= 7) return "stark bewölkt";
  return "bedeckt";
}

export interface Tendenz {
  wort: string;
  kurz: string; // für 1x1 und 2x1
  pfeil: string; // Font-Awesome-Klasse
}

/** Luftdrucktendenz über 3 Stunden; unter DRUCK_STABIL_HPA gilt sie als gleichbleibend (wie am Desktop). */
export function druckTendenz(hpa: number | null): Tendenz | null {
  if (hpa === null) return null;
  if (hpa > DRUCK_STABIL_HPA) return { wort: "steigt", kurz: "steigt", pfeil: "fa-arrow-trend-up" };
  if (hpa < -DRUCK_STABIL_HPA) return { wort: "fällt", kurz: "fällt", pfeil: "fa-arrow-trend-down" };
  return { wort: "gleichbleibend", kurz: "stabil", pfeil: "fa-arrow-right-long" };
}

const ganz = (v: number) => zahl(v);
const ohne = () => "";
type Eintrag = Omit<Messwert, "art" | "titel">;

const WERTE: Record<string, Eintrag> = {
  gefuehlt: {
    kurz: "Gefühlt",
    symbol: "fa-temperature-half",
    einheit: "",
    einheitVerlauf: "°",
    farbe: "temp",
    flaeche: false,
    saeulen: false,
    jetzt: (d) => d.jetzt?.gefuehlt ?? null,
    stunde: (s) => s.gefuehlt,
    text: grad,
    klasse: tempKlasse,
    zusatz: (d) => (d.jetzt ? { text: "gemessen", fett: grad(d.jetzt.temp) } : { text: "" }),
  },
  feuchte: {
    kurz: "Feuchte",
    symbol: "fa-droplet",
    einheit: "%",
    einheitVerlauf: " %",
    farbe: "--regen",
    flaeche: true,
    saeulen: false,
    jetzt: (d) => d.jetzt?.feuchte ?? null,
    stunde: (s) => s.feuchte,
    text: ganz,
    klasse: ohne,
    zusatz: (d) => (d.jetzt ? { text: "Taupunkt", fett: grad(d.jetzt.taupunkt) } : { text: "" }),
  },
  taupunkt: {
    kurz: "Taupunkt",
    symbol: "fa-temperature-low",
    einheit: "",
    einheitVerlauf: "°",
    farbe: "--text-2",
    flaeche: false,
    saeulen: false,
    jetzt: (d) => d.jetzt?.taupunkt ?? null,
    stunde: (s) => s.taupunkt,
    text: grad,
    klasse: ohne,
    zusatz: (d) => (d.jetzt ? { text: "Feuchte", fett: `${zahl(d.jetzt.feuchte)} %` } : { text: "" }),
  },
  druck: {
    kurz: "Luftdruck",
    symbol: "fa-gauge",
    einheit: "",
    einheitVerlauf: "",
    farbe: "--text-2",
    flaeche: false,
    saeulen: false,
    jetzt: (d) => d.jetzt?.druck ?? null,
    stunde: (s) => s.druck,
    text: ganz,
    klasse: ohne,
    zusatz: (d, _, eng) => {
      const t = druckTendenz(d.jetzt?.druck_tendenz ?? null);
      return { text: t ? `hPa, ${eng ? t.kurz : t.wort}` : "hPa" };
    },
  },
  sicht: {
    kurz: "Sicht",
    symbol: "fa-eye",
    einheit: "km",
    einheitVerlauf: " km",
    farbe: "--text-2",
    flaeche: false,
    saeulen: false,
    jetzt: (d) => d.jetzt?.sicht_km ?? null,
    stunde: (s) => s.sicht_km,
    text: (v) => zahl(v, v < 10 ? 1 : 0),
    klasse: ohne,
    zusatz: (_, v) => ({ text: sichtWort(v) }),
  },
  bewoelkung: {
    kurz: "Wolken",
    symbol: "fa-cloud",
    einheit: "%",
    einheitVerlauf: " %",
    farbe: "--text-2",
    flaeche: true,
    saeulen: false,
    jetzt: (d) => d.jetzt?.bewoelkung ?? null,
    stunde: (s) => s.bewoelkung,
    text: ganz,
    klasse: ohne,
    zusatz: (_, v) => ({ text: wolkenWort(v) }),
  },
  regen_heute: {
    kurz: "Regen",
    symbol: "fa-cloud-rain",
    einheit: "mm",
    einheitVerlauf: "",
    farbe: "--regen",
    flaeche: false,
    saeulen: true,
    jetzt: (d) => d.tage[0]?.regen_mm ?? null,
    stunde: (s) => s.regen_mm,
    text: (v) => zahl(v, 1),
    klasse: () => "c-regen",
    zusatz: () => ({ text: "heute" }),
  },
  boeen: {
    kurz: "Böen",
    symbol: "fa-wind",
    einheit: "km/h",
    einheitVerlauf: "",
    farbe: "--text-2",
    flaeche: false,
    saeulen: false,
    jetzt: (d) => d.jetzt?.boeen ?? null,
    stunde: (s) => s.boeen,
    text: ganz,
    klasse: ohne,
    zusatz: (d) => (d.jetzt ? { text: `aus ${richtungLang(d.jetzt.wind_grad)}` } : { text: "" }),
  },
};

const auswahl = telefonKatalog.typen.messwert?.einstellungen.find((e) => e.schluessel === "groesse");

/** Messwert zu einem Wert der Einstellung; Unbekanntes fällt auf den Standard des Katalogs zurück. */
export function messwertVon(art: string): Messwert {
  const gilt = WERTE[art] ? art : String(auswahl?.standard ?? "feuchte");
  const titel = auswahl?.optionen.find((o) => o.wert === gilt)?.titel ?? gilt;
  return { art: gilt, titel, ...WERTE[gilt] };
}

/** Verlauf um die laufende Stunde: zurück und voraus in Stunden. null, wenn ein Wert fehlt. */
export function verlauf(d: Kompakt, m: Messwert, zurueck: number, voraus: number): { werte: number[]; jetzt: number } | null {
  const von = Math.max(0, d.jetzt_index - zurueck);
  const werte = d.stunden.slice(von, d.jetzt_index + voraus + 1).map(m.stunde);
  if (werte.length < 2 || werte.some((v) => v === null)) return null;
  return { werte: werte as number[], jetzt: d.jetzt_index - von };
}

// Wache: jeder Wert des Katalogs braucht hier einen Eintrag (fällt in der Entwicklung sofort auf).
for (const o of auswahl?.optionen ?? []) {
  if (!WERTE[o.wert]) console.error(`Messwert ohne Eintrag: ${o.wert}`);
}
