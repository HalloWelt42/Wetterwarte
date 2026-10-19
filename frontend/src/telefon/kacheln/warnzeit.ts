// Zeitraum einer Warnung in Ortszeit, kurz und ohne Datum, wo es nicht nötig ist:
// "bis 19 Uhr" (gilt schon), "heute 15 bis 19 Uhr", "heute 22 bis morgen 6 Uhr".
import { tageBis, teile } from "../../kern/zeit";

/** Uhrzeit ohne Minuten, wenn sie voll ist ("15", "15:30"). */
function uhr(zeit: string, zone: string): string {
  const t = teile(zeit, zone);
  return t.minute === 0 ? String(t.stunde) : `${t.stunde}:${String(t.minute).padStart(2, "0")}`;
}

/** "heute", "morgen" oder das Datum ("21.10.", am Satzanfang "am 21.10."). */
function tag(zeit: string, jetzt: Date, zone: string, am = false): string {
  const abstand = tageBis(zeit, jetzt, zone);
  if (abstand === 0) return "heute";
  if (abstand === 1) return "morgen";
  const t = teile(zeit, zone);
  return `${am ? "am " : ""}${t.tag}.${t.monat}.`;
}

export function warnZeitraum(von: string | null, bis: string | null, jetzt: Date, zone: string): string {
  const ende = bis && (tageBis(bis, jetzt, zone) === 0 ? `${uhr(bis, zone)} Uhr` : `${tag(bis, jetzt, zone)} ${uhr(bis, zone)} Uhr`);
  // Gilt schon: nur noch das Ende zählt
  if (!von || Date.parse(von) <= jetzt.getTime()) return ende ? `bis ${ende}` : "gilt jetzt";
  if (!bis) return `ab ${tag(von, jetzt, zone)} ${uhr(von, zone)} Uhr`;
  const beginn = `${tag(von, jetzt, zone, true)} ${uhr(von, zone)}`;
  return tageBis(von, jetzt, zone) === tageBis(bis, jetzt, zone) ? `${beginn} bis ${uhr(bis, zone)} Uhr` : `${beginn} bis ${ende}`;
}
