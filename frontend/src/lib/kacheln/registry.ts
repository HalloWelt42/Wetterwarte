// Kachel-Registry: die einzige Wahrheit über die Desktop-Kacheltypen (Komponente, Daten,
// Hilfethema, Größe, Einstellungen). Katalog, Brett und Kachelhülle lesen nur von hier.

export interface Feld {
  art: "mehrfach" | "auswahl" | "zahl" | "schalter" | "zeitzone";
  schluessel: string;
  label: string;
  optionen?: { wert: string | number; label: string }[];
  min?: number;
  max?: number;
  schritt?: number;
  einheit?: string;
  // Bei "mehrfach": ist die Standardauswahl leer (z.B. Allergien) statt "alle"?
  leerStandard?: boolean;
}

import type { Component } from "svelte";
import type { BereichName } from "../ortdaten.svelte";
import Aktuell from "./typen/Aktuell.svelte";
import Barometer from "./typen/Barometer.svelte";
import Blitze from "./typen/Blitze.svelte";
import Jahresmesswerte from "./typen/Jahresmesswerte.svelte";
import Kalender from "./typen/Kalender.svelte";
import Karte from "./typen/Karte.svelte";
import Klima from "./typen/Klima.svelte";
import Luftqualitaet from "./typen/Luftqualitaet.svelte";
import Mond from "./typen/Mond.svelte";
import Nowcast from "./typen/Nowcast.svelte";
import Pollen from "./typen/Pollen.svelte";
import Sonne from "./typen/Sonne.svelte";
import Stunden from "./typen/Stunden.svelte";
import Tage from "./typen/Tage.svelte";
import Uhr from "./typen/Uhr.svelte";
import Uv from "./typen/Uv.svelte";
import Verlauf from "./typen/Verlauf.svelte";
import Warnungen from "./typen/Warnungen.svelte";
import Wind from "./typen/Wind.svelte";

export interface KachelDef {
  typ: string;
  /** Datenbereiche, die die Kachel braucht; die Hülle zeigt Laden, Ausfall oder Alter. */
  bereiche: readonly BereichName[];
  /** Hinweis bei Ausfall, wenn der allgemeine nicht passt. */
  fehltHinweis?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  komponente: Component<any>;
  hilfe: string; // Hilfethema für den Hilfepunkt im Kachelkopf
  titel: string;
  icon: string; // Font-Awesome-Klasse
  w: number;
  h: number;
  familie: string;
  unter?: string; // Untertitel; "ORT" wird durch den aktiven Ort ersetzt
  einstellungen?: Feld[]; // typ-spezifische Optionen (im Einstellungs-Modal)
}

const KENNZAHLEN = [
  { wert: "feuchte", label: "Feuchte" },
  { wert: "wind", label: "Wind" },
  { wert: "druck", label: "Druck" },
  { wert: "sicht", label: "Sicht" },
  { wert: "taupunkt", label: "Taupunkt" },
  { wert: "bewoelkung", label: "Bewölkung" },
];

const POLLEN_ARTEN = [
  { wert: "Hasel", label: "Hasel" },
  { wert: "Erle", label: "Erle" },
  { wert: "Esche", label: "Esche" },
  { wert: "Birke", label: "Birke" },
  { wert: "Gräser", label: "Gräser" },
  { wert: "Roggen", label: "Roggen" },
  { wert: "Beifuß", label: "Beifuß" },
  { wert: "Ambrosia", label: "Ambrosia" },
];

const SCHADSTOFFE = [
  { wert: "pm2_5", label: "PM2,5" },
  { wert: "pm10", label: "PM10" },
  { wert: "o3", label: "Ozon" },
  { wert: "no2", label: "NO₂" },
];

export const registry: Record<string, KachelDef> = {
  aktuell: {
    typ: "aktuell", komponente: Aktuell, hilfe: "kacheln", bereiche: ["basis"], titel: "Aktuell", icon: "fa-temperature-half", w: 4, h: 3, familie: "Wetter", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "kennzahlen", label: "Angezeigte Kennzahlen", optionen: KENNZAHLEN }],
  },
  stunden: {
    typ: "stunden", komponente: Stunden, hilfe: "kacheln", bereiche: ["basis"], titel: "Stundenvorhersage", icon: "fa-clock", w: 8, h: 3, familie: "Wetter", unter: "bis 18 Stunden",
    einstellungen: [
      {
        art: "auswahl", schluessel: "anzahl", label: "Zeitraum",
        optionen: [{ wert: 8, label: "8 Stunden" }, { wert: 12, label: "12 Stunden" }, { wert: 18, label: "18 Stunden" }],
      },
    ],
  },
  tage: {
    typ: "tage", komponente: Tage, hilfe: "kacheln", bereiche: ["basis"], titel: "7-Tage-Vorhersage", icon: "fa-calendar-days", w: 4, h: 4, familie: "Wetter",
    einstellungen: [
      { art: "auswahl", schluessel: "anzahl", label: "Zeitraum", optionen: [{ wert: 5, label: "5 Tage" }, { wert: 7, label: "7 Tage" }] },
    ],
  },
  warnungen: { typ: "warnungen", komponente: Warnungen, hilfe: "kacheln", bereiche: ["warnungen"], fehltHinweis: "Warnlage unbekannt: die Warnquelle antwortet gerade nicht.", titel: "Wetterwarnungen", icon: "fa-triangle-exclamation", w: 4, h: 2, familie: "Umwelt", unter: "amtlich" },
  karte: { typ: "karte", komponente: Karte, hilfe: "karte", bereiche: [], titel: "Karte", icon: "fa-map-location-dot", w: 4, h: 4, familie: "Karte", unter: "Live-Blitze" },
  nowcast: { typ: "nowcast", komponente: Nowcast, hilfe: "diagramme", bereiche: ["basis"], titel: "Regen-Nowcast", icon: "fa-cloud-showers-heavy", w: 4, h: 2, familie: "Karte", unter: "ORT" },
  blitze: { typ: "blitze", komponente: Blitze, hilfe: "kacheln", bereiche: ["blitze"], titel: "Blitze", icon: "fa-bolt", w: 4, h: 2, familie: "Karte", unter: "Umkreis 130 km" },
  wind: { typ: "wind", komponente: Wind, hilfe: "kacheln", bereiche: ["basis"], titel: "Wind", icon: "fa-wind", w: 4, h: 2, familie: "Detail" },
  sonne: { typ: "sonne", komponente: Sonne, hilfe: "zeit", bereiche: ["basis"], titel: "Sonne", icon: "fa-sun", w: 4, h: 3, familie: "Umwelt" },
  mond: { typ: "mond", komponente: Mond, hilfe: "zeit", bereiche: [], titel: "Mond", icon: "fa-moon", w: 4, h: 2, familie: "Umwelt" },
  luftqualitaet: {
    typ: "luftqualitaet", komponente: Luftqualitaet, hilfe: "kacheln", bereiche: ["luft"], titel: "Luftqualität", icon: "fa-smog", w: 4, h: 2, familie: "Umwelt", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "schadstoffe", label: "Angezeigte Schadstoffe", optionen: SCHADSTOFFE }],
  },
  uv: { typ: "uv", komponente: Uv, hilfe: "kacheln", bereiche: ["basis"], titel: "UV-Index", icon: "fa-sun", w: 4, h: 2, familie: "Umwelt" },
  pollen: {
    typ: "pollen", komponente: Pollen, hilfe: "kacheln", bereiche: ["pollen"], titel: "Pollenflug", icon: "fa-seedling", w: 4, h: 5, familie: "Umwelt", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "allergien", label: "Meine Allergien (hervorheben)", optionen: POLLEN_ARTEN, leerStandard: true }],
  },
  barometer: { typ: "barometer", komponente: Barometer, hilfe: "diagramme", bereiche: ["basis"], titel: "Luftdruck", icon: "fa-gauge", w: 4, h: 3, familie: "Detail" },
  verlauf: { typ: "verlauf", komponente: Verlauf, hilfe: "diagramme", bereiche: ["basis"], titel: "Temperaturverlauf", icon: "fa-chart-line", w: 8, h: 3, familie: "Archiv", unter: "24 Stunden" },
  klima: { typ: "klima", komponente: Klima, hilfe: "archiv", bereiche: [], titel: "Klima-Diagramm", icon: "fa-chart-column", w: 6, h: 4, familie: "Archiv", unter: "Monatsnormale" },
  jahresmesswerte: {
    typ: "jahresmesswerte", komponente: Jahresmesswerte, hilfe: "archiv", bereiche: [], titel: "Jahresmesswerte", icon: "fa-chart-simple", w: 6, h: 4, familie: "Archiv", unter: "ORT",
    einstellungen: [
      {
        art: "auswahl", schluessel: "variable", label: "Messgröße",
        optionen: [
          { wert: "temperatur", label: "Temperatur" },
          { wert: "feuchte", label: "Luftfeuchte" },
          { wert: "wind", label: "Wind" },
          { wert: "druck", label: "Luftdruck" },
          { wert: "aqi", label: "Luftgüte (AQI)" },
          { wert: "pm2_5", label: "Feinstaub PM2,5" },
          { wert: "pm10", label: "Feinstaub PM10" },
          { wert: "o3", label: "Ozon" },
          { wert: "no2", label: "Stickstoffdioxid" },
        ],
      },
    ],
  },
  uhr: {
    typ: "uhr", komponente: Uhr, hilfe: "zeit", bereiche: [], titel: "Uhr", icon: "fa-clock", w: 4, h: 2, familie: "Rahmen",
    einstellungen: [
      {
        art: "auswahl", schluessel: "variante", label: "Darstellung",
        optionen: [{ wert: "analog", label: "Analog" }, { wert: "gross", label: "Groß" }, { wert: "digital", label: "Digital" }],
      },
      { art: "zeitzone", schluessel: "zeitzone", label: "Zeitzone" },
    ],
  },
  kalender: {
    typ: "kalender", komponente: Kalender, hilfe: "zeit", bereiche: [], titel: "Kalender", icon: "fa-calendar-days", w: 4, h: 3, familie: "Rahmen",
    einstellungen: [
      {
        art: "auswahl", schluessel: "variante", label: "Darstellung",
        optionen: [{ wert: "tag", label: "Tag" }, { wert: "monat", label: "Monat" }],
      },
    ],
  },
};

export const standardKacheln = [
  "aktuell", "stunden", "warnungen", "karte", "tage", "nowcast",
  "wind", "sonne", "mond", "luftqualitaet", "uv", "barometer", "verlauf",
  "blitze", "pollen",
];

export const familien = ["Wetter", "Karte", "Umwelt", "Detail", "Archiv", "Rahmen"];
