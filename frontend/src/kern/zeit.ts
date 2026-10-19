// Zeit in der Zeitzone eines Orts, ohne den Umweg über toLocaleString und new Date
// (der verliert Sommerzeitwechsel und Sekunden). Alles über Intl.formatToParts.

const formate = new Map<string, Intl.DateTimeFormat>();

function format(zone: string, optionen: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
  const k = zone + JSON.stringify(optionen);
  let f = formate.get(k);
  if (!f) {
    f = new Intl.DateTimeFormat("de-DE", { timeZone: zone || undefined, ...optionen });
    formate.set(k, f);
  }
  return f;
}

export interface Teile {
  jahr: number;
  monat: number; // 1 bis 12
  tag: number;
  stunde: number;
  minute: number;
  wochentag: number; // 0 Sonntag bis 6 Samstag
}

const WOCHENTAGE = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];

export function teile(zeit: Date | string, zone: string): Teile {
  const d = typeof zeit === "string" ? new Date(zeit) : zeit;
  const p = Object.fromEntries(
    format(zone, { year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric", weekday: "short", hourCycle: "h23" })
      .formatToParts(d)
      .map((t) => [t.type, t.value]),
  );
  return {
    jahr: +p.year,
    monat: +p.month,
    tag: +p.day,
    stunde: +p.hour,
    minute: +p.minute,
    wochentag: WOCHENTAGE.indexOf(String(p.weekday).replace(".", "")),
  };
}

/** "14:20" in der Zeitzone des Orts. */
export function uhrzeit(zeit: Date | string, zone: string): string {
  const t = teile(zeit, zone);
  return `${String(t.stunde).padStart(2, "0")}:${String(t.minute).padStart(2, "0")}`;
}

/** Stunde als Zahl in der Zeitzone des Orts. */
export function stunde(zeit: Date | string, zone: string): number {
  return teile(zeit, zone).stunde;
}

export function wochentagKurz(zeit: Date | string, zone: string): string {
  return WOCHENTAGE[teile(zeit, zone).wochentag] ?? "";
}

/** Minuten seit Mitternacht in der Zeitzone des Orts. */
export function minutenAmTag(zeit: Date | string, zone: string): number {
  const t = teile(zeit, zone);
  return t.stunde * 60 + t.minute;
}

/** Abstand zu einem Zeitpunkt: "vor 3 Minuten", "vor 2 Stunden". Mit kurz für enge Marken
 *  ("vor 3 Min", "vor 2 h"). */
export function vorZeit(iso: string | null, jetzt: Date, kurz = false): string {
  if (!iso) return "";
  const min = Math.max(0, Math.round((jetzt.getTime() - new Date(iso).getTime()) / 60000));
  if (min < 1) return "gerade eben";
  if (min < 60) return kurz ? `vor ${min} Min` : `vor ${min} ${min === 1 ? "Minute" : "Minuten"}`;
  const h = Math.round(min / 60);
  if (h < 48) return kurz ? `vor ${h} h` : `vor ${h} ${h === 1 ? "Stunde" : "Stunden"}`;
  return `vor ${Math.round(h / 24)} Tagen`;
}

/** Kalendertag eines Zeitpunkts in der Zeitzone des Orts als "2026-10-19" (wie Tag.datum). */
export function kalendertag(zeit: Date | string, zone: string): string {
  const t = teile(zeit, zone);
  return `${t.jahr}-${String(t.monat).padStart(2, "0")}-${String(t.tag).padStart(2, "0")}`;
}

/** Fortlaufende Nummer des Kalendertags in der Zeitzone des Orts. */
export function tagNummer(zeit: Date | string, zone: string): number {
  const t = teile(zeit, zone);
  return Date.UTC(t.jahr, t.monat - 1, t.tag) / 86_400_000;
}

/** Kalendertage von jetzt bis zeit in der Zeitzone des Orts (0 heute, 1 morgen, -1 gestern). */
export function tageBis(zeit: Date | string, jetzt: Date, zone: string): number {
  return tagNummer(zeit, zone) - tagNummer(jetzt, zone);
}
