// Kachel-Registry: die Wahrheit ueber verfuegbare Kacheltypen. Der Katalog und
// das Brett werden daraus gespeist; neue Typen hier + in KachelKoerper ergaenzen.

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

export interface KachelDef {
  typ: string;
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
    typ: "aktuell", titel: "Aktuell", icon: "fa-temperature-half", w: 4, h: 3, familie: "Wetter", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "kennzahlen", label: "Angezeigte Kennzahlen", optionen: KENNZAHLEN }],
  },
  stunden: {
    typ: "stunden", titel: "Stundenvorhersage", icon: "fa-clock", w: 8, h: 3, familie: "Wetter", unter: "48 Stunden",
    einstellungen: [
      {
        art: "auswahl", schluessel: "anzahl", label: "Zeitraum",
        optionen: [{ wert: 8, label: "8 Stunden" }, { wert: 12, label: "12 Stunden" }, { wert: 18, label: "18 Stunden" }],
      },
    ],
  },
  tage: {
    typ: "tage", titel: "7-Tage-Vorhersage", icon: "fa-calendar-days", w: 4, h: 4, familie: "Wetter",
    einstellungen: [
      { art: "auswahl", schluessel: "anzahl", label: "Zeitraum", optionen: [{ wert: 5, label: "5 Tage" }, { wert: 7, label: "7 Tage" }] },
    ],
  },
  warnungen: { typ: "warnungen", titel: "Wetterwarnungen", icon: "fa-triangle-exclamation", w: 4, h: 2, familie: "Umwelt", unter: "amtlich" },
  karte: { typ: "karte", titel: "Karte", icon: "fa-map-location-dot", w: 4, h: 4, familie: "Karte", unter: "Live-Blitze" },
  nowcast: { typ: "nowcast", titel: "Regen-Nowcast", icon: "fa-cloud-showers-heavy", w: 4, h: 2, familie: "Karte", unter: "ORT" },
  blitze: { typ: "blitze", titel: "Blitze", icon: "fa-bolt", w: 4, h: 2, familie: "Karte", unter: "Umkreis 130 km" },
  wind: { typ: "wind", titel: "Wind", icon: "fa-wind", w: 4, h: 2, familie: "Detail" },
  sonne: { typ: "sonne", titel: "Sonne", icon: "fa-sun", w: 4, h: 3, familie: "Umwelt" },
  mond: { typ: "mond", titel: "Mond", icon: "fa-moon", w: 4, h: 2, familie: "Umwelt" },
  luftqualitaet: {
    typ: "luftqualitaet", titel: "Luftqualität", icon: "fa-smog", w: 4, h: 2, familie: "Umwelt", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "schadstoffe", label: "Angezeigte Schadstoffe", optionen: SCHADSTOFFE }],
  },
  uv: { typ: "uv", titel: "UV-Index", icon: "fa-sun", w: 4, h: 2, familie: "Umwelt" },
  pollen: {
    typ: "pollen", titel: "Pollenflug", icon: "fa-seedling", w: 4, h: 5, familie: "Umwelt", unter: "ORT",
    einstellungen: [{ art: "mehrfach", schluessel: "allergien", label: "Meine Allergien (hervorheben)", optionen: POLLEN_ARTEN, leerStandard: true }],
  },
  barometer: { typ: "barometer", titel: "Luftdruck", icon: "fa-gauge", w: 4, h: 3, familie: "Detail" },
  verlauf: { typ: "verlauf", titel: "Temperaturverlauf", icon: "fa-chart-line", w: 8, h: 3, familie: "Archiv", unter: "24 Stunden" },
  uhr: {
    typ: "uhr", titel: "Uhr", icon: "fa-clock", w: 4, h: 2, familie: "Rahmen",
    einstellungen: [
      {
        art: "auswahl", schluessel: "variante", label: "Darstellung",
        optionen: [{ wert: "analog", label: "Analog" }, { wert: "gross", label: "Groß" }, { wert: "digital", label: "Digital" }],
      },
      { art: "zeitzone", schluessel: "zeitzone", label: "Zeitzone" },
    ],
  },
  kalender: {
    typ: "kalender", titel: "Kalender", icon: "fa-calendar-days", w: 4, h: 3, familie: "Rahmen",
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
