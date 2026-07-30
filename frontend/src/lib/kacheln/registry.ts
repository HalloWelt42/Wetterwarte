// Kachel-Registry: die Wahrheit ueber verfuegbare Kacheltypen. Der Katalog und
// das Brett werden daraus gespeist; neue Typen hier + in KachelKoerper ergaenzen.

export interface KachelDef {
  typ: string;
  titel: string;
  icon: string; // Font-Awesome-Klasse
  w: number;
  h: number;
  familie: string;
  unter?: string; // Untertitel; "ORT" wird durch den aktiven Ort ersetzt
}

export const registry: Record<string, KachelDef> = {
  aktuell: { typ: "aktuell", titel: "Aktuell", icon: "fa-temperature-half", w: 4, h: 3, familie: "Wetter", unter: "ORT" },
  stunden: { typ: "stunden", titel: "Stundenvorhersage", icon: "fa-clock", w: 8, h: 3, familie: "Wetter", unter: "48 Stunden" },
  tage: { typ: "tage", titel: "7-Tage-Vorhersage", icon: "fa-calendar-days", w: 4, h: 4, familie: "Wetter" },
  warnungen: { typ: "warnungen", titel: "Wetterwarnungen", icon: "fa-triangle-exclamation", w: 4, h: 2, familie: "Umwelt", unter: "amtlich" },
  karte: { typ: "karte", titel: "Karte", icon: "fa-map-location-dot", w: 4, h: 4, familie: "Karte", unter: "Radar" },
  nowcast: { typ: "nowcast", titel: "Regen-Nowcast", icon: "fa-cloud-showers-heavy", w: 4, h: 2, familie: "Karte", unter: "ORT" },
  blitze: { typ: "blitze", titel: "Blitze", icon: "fa-bolt", w: 4, h: 2, familie: "Karte", unter: "Umkreis 130 km" },
  wind: { typ: "wind", titel: "Wind", icon: "fa-wind", w: 4, h: 2, familie: "Detail" },
  sonnemond: { typ: "sonnemond", titel: "Sonne und Mond", icon: "fa-sun", w: 4, h: 2, familie: "Umwelt" },
  luftqualitaet: { typ: "luftqualitaet", titel: "Luftqualität", icon: "fa-smog", w: 4, h: 2, familie: "Umwelt", unter: "ORT" },
  uv: { typ: "uv", titel: "UV-Index", icon: "fa-sun", w: 4, h: 2, familie: "Umwelt" },
  pollen: { typ: "pollen", titel: "Pollenflug", icon: "fa-seedling", w: 4, h: 2, familie: "Umwelt", unter: "ORT" },
  barometer: { typ: "barometer", titel: "Luftdruck", icon: "fa-gauge", w: 4, h: 2, familie: "Detail" },
  verlauf: { typ: "verlauf", titel: "Temperaturverlauf", icon: "fa-chart-line", w: 8, h: 2, familie: "Archiv", unter: "Archiv" },
};

export const standardKacheln = [
  "aktuell", "stunden", "warnungen", "karte", "tage", "nowcast",
  "wind", "sonnemond", "luftqualitaet", "uv", "barometer", "verlauf",
  "blitze", "pollen",
];

export const familien = ["Wetter", "Karte", "Umwelt", "Detail", "Archiv"];
