// Datums- und Dauerangaben der Detailblätter. Zeitpunkte immer in der Zeitzone des Orts
// (über kern/zeit.ts); Kalendertage ("2026-10-20") stehen fest und brauchen keine Zone.
import { kalendertag, uhrzeit } from "../../kern/zeit";

export { kalendertag };

export const WOCHENTAGE = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
export const MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];

const zwei = (n: number) => String(n).padStart(2, "0");

function zerlege(datum: string): [number, number, number] {
  const [j, m, t] = datum.split("-").map(Number);
  return [j, m, t];
}


/** Wochentag eines Kalendertags in Worten ("Dienstag"). */
export function wochentag(datum: string): string {
  const [j, m, t] = zerlege(datum);
  return WOCHENTAGE[new Date(Date.UTC(j, m - 1, t)).getUTCDay()];
}

/** "20.10." zu einem Kalendertag. */
export function tagMonat(datum: string): string {
  const [, m, t] = zerlege(datum);
  return `${t}.${m}.`;
}

/** "Dienstag 20.10." zu einem Kalendertag. */
export function tagLang(datum: string): string {
  return `${wochentag(datum)} ${tagMonat(datum)}`;
}

/** Ganze Tage von Kalendertag a bis b (b später: positiv). */
export function tageZwischen(a: string, b: string): number {
  const [ja, ma, ta] = zerlege(a);
  const [jb, mb, tb] = zerlege(b);
  return Math.round((Date.UTC(jb, mb - 1, tb) - Date.UTC(ja, ma - 1, ta)) / 86_400_000);
}

/** "heute", "morgen", "übermorgen" oder "Dienstag 20.10." (klein, für den Gebrauch im Satz). */
export function tagNah(datum: string, heute: string): string {
  const d = tageZwischen(heute, datum);
  if (d === 0) return "heute";
  if (d === 1) return "morgen";
  if (d === 2) return "übermorgen";
  if (d === -1) return "gestern";
  return tagLang(datum);
}

/** Erster Buchstabe groß (Satzanfang). */
export function gross(text: string): string {
  return text ? text[0].toUpperCase() + text.slice(1) : text;
}

/** Zeitpunkt als "heute 14:00" oder "Dienstag 20.10. 06:00" in Ortszeit. */
export function tagUndUhr(zeit: string, zone: string, heute: string): string {
  return `${tagNah(kalendertag(zeit, zone), heute)} ${uhrzeit(zeit, zone)}`;
}

/** Gültigkeit einer Warnung in Ortszeit, etwa "heute 14:00 bis 22:00 Uhr". */
export function zeitraum(von: string | null, bis: string | null, zone: string, heute: string): string {
  if (!von && !bis) return "ohne Zeitangabe";
  if (von && !bis) return `ab ${tagUndUhr(von, zone, heute)} Uhr, ohne Ende`;
  if (!von && bis) return `bis ${tagUndUhr(bis, zone, heute)} Uhr`;
  const gleicherTag = kalendertag(von!, zone) === kalendertag(bis!, zone);
  const ende = gleicherTag ? uhrzeit(bis!, zone) : tagUndUhr(bis!, zone, heute);
  return `${tagUndUhr(von!, zone, heute)} bis ${ende} Uhr`;
}

/** Dauer in Worten: "10 Stunden 20 Minuten", "25 Minuten", "1 Stunde". */
export function dauerLang(sekunden: number): string {
  const min = Math.round(Math.abs(sekunden) / 60);
  const h = Math.floor(min / 60);
  const m = min % 60;
  const teil = [h ? `${h} ${h === 1 ? "Stunde" : "Stunden"}` : "", m || !h ? `${m} ${m === 1 ? "Minute" : "Minuten"}` : ""];
  return teil.filter(Boolean).join(" ");
}

/** Abstand zu einem vergangenen Zeitpunkt ausgeschrieben: "vor 3 Minuten", "vor 2 Stunden". */
export function vorLang(zeit: string, jetzt: Date): string {
  const min = Math.max(0, Math.round((jetzt.getTime() - new Date(zeit).getTime()) / 60_000));
  if (min < 1) return "gerade eben";
  if (min < 60) return `vor ${min} ${min === 1 ? "Minute" : "Minuten"}`;
  const h = Math.round(min / 60);
  if (h < 48) return `vor ${h} ${h === 1 ? "Stunde" : "Stunden"}`;
  return `vor ${Math.round(h / 24)} Tagen`;
}

/** Versatz zur Weltzeit in Minuten aus einer ISO-Zeit mit Versatz ("+02:00" ergibt 120). */
export function versatzMinuten(iso: string): number | null {
  const m = /([+-])(\d{2}):(\d{2})$/.exec(iso);
  if (!m) return iso.endsWith("Z") ? 0 : null;
  return (m[1] === "-" ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3]));
}
