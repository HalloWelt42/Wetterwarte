// Platzhalterdaten fuer das Dashboard - identisch zur Design-Vorlage.
// Wird spaeter durch echte Daten (eigener DWD-Ingester, Open-Meteo) ersetzt;
// die Form bleibt gleich.
import type { Aktuell, OrtEintrag, Stunde, Tag, Warnung } from "./typen";

export const orte: OrtEintrag[] = [
  { name: "Köln", region: "Sachsen-Anhalt", icon: "partly-cloudy-day", temp: 24, aktiv: true },
  { name: "Frankfurt", region: "Sachsen", icon: "clear-day", temp: 26 },
  { name: "Berlin", region: "Berlin", icon: "overcast-day", temp: 22 },
  { name: "Hamburg", region: "Hamburg", icon: "rain", temp: 19 },
  { name: "München", region: "Bayern", icon: "thunderstorms-day", temp: 21 },
];

export const aktuell: Aktuell = {
  temperatur: 24,
  tempKlasse: "t-warm",
  gefuehlt: 26,
  tageshoch: 27,
  zustandText: "Wolkig, später Schauer",
  icon: "partly-cloudy-day",
  feuchte: 68,
  wind: 14,
  windRichtung: "NW",
  druck: 1012,
  sicht: 24,
  taupunkt: 17,
  bewoelkung: 60,
};

export const stunden: Stunde[] = [
  { zeit: "jetzt", icon: "partly-cloudy-day", temp: 24, tempKlasse: "t-warm" },
  { zeit: "15", icon: "clear-day", temp: 25, tempKlasse: "t-warm" },
  { zeit: "16", icon: "partly-cloudy-day", temp: 25, tempKlasse: "t-heiss", regen: 10 },
  { zeit: "17", icon: "overcast-day", temp: 24, tempKlasse: "t-warm", regen: 30 },
  { zeit: "18", icon: "thunderstorms-day-rain", temp: 23, tempKlasse: "t-warm", regen: 70 },
  { zeit: "19", icon: "rain", temp: 21, tempKlasse: "t-mild", regen: 65 },
  { zeit: "20", icon: "drizzle", temp: 20, tempKlasse: "t-mild", regen: 55 },
  { zeit: "21", icon: "partly-cloudy-night", temp: 19, tempKlasse: "t-mild", regen: 30 },
  { zeit: "22", icon: "clear-night", temp: 18, tempKlasse: "t-mild" },
  { zeit: "23", icon: "clear-night", temp: 18, tempKlasse: "t-mild" },
  { zeit: "00", icon: "partly-cloudy-night", temp: 17, tempKlasse: "t-kuehl" },
  { zeit: "01", icon: "partly-cloudy-night", temp: 17, tempKlasse: "t-kuehl" },
  { zeit: "02", icon: "fog-night", temp: 16, tempKlasse: "t-kuehl" },
  { zeit: "03", icon: "fog-night", temp: 16, tempKlasse: "t-kuehl" },
  { zeit: "04", icon: "clear-night", temp: 15, tempKlasse: "t-kuehl" },
  { zeit: "05", icon: "sunrise", temp: 16, tempKlasse: "t-kuehl" },
  { zeit: "06", icon: "clear-day", temp: 18, tempKlasse: "t-mild" },
  { zeit: "07", icon: "clear-day", temp: 20, tempKlasse: "t-mild" },
];

export const tage: Tag[] = [
  { kurz: "Heute", icon: "thunderstorms-day-rain", hi: 27, lo: 15, bandLinks: 30, bandRechts: 8 },
  { kurz: "Mi", icon: "rain", hi: 23, lo: 14, bandLinks: 22, bandRechts: 20 },
  { kurz: "Do", icon: "partly-cloudy-day", hi: 26, lo: 15, bandLinks: 26, bandRechts: 10 },
  { kurz: "Fr", icon: "clear-day", hi: 29, lo: 16, bandLinks: 30, bandRechts: 4 },
  { kurz: "Sa", icon: "clear-day", hi: 31, lo: 18, bandLinks: 34, bandRechts: 2 },
  { kurz: "So", icon: "overcast-day", hi: 25, lo: 17, bandLinks: 28, bandRechts: 12 },
  { kurz: "Mo", icon: "drizzle", hi: 24, lo: 15, bandLinks: 24, bandRechts: 16 },
];

export const warnungen: Warnung[] = [
  { stufe: 3, titel: "Markantes Gewitter", zeit: "Heute 17:00 - 21:00 Uhr - Stufe 3", icon: "thunderstorms-day" },
  { stufe: 1, titel: "Windböen bis 60 km/h", zeit: "Heute 16:00 - 22:00 Uhr - Stufe 1", faIcon: "fa-wind" },
];
