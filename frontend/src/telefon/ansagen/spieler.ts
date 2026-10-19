// Ansagen abspielen (docs/WARNUNGEN.md): ein Gong aus Web Audio, dann die vertonten Sätze (MP3 aus dem Medienpool,
// tools/ansagen.py) mit kurzer Pause. Web Audio statt <audio>: das iPhone spielt Ton ohne Berührung nur über einen
// Kontext, der in einer Berührung freigeschaltet wurde; danach darf die App von selbst sprechen, solange sie offen
// ist. Angehalten wird über die Quellen, nie durch Entfernen von Elementen.
import { meldekatalog } from "../../kern/gemeinsam";

const klaenge = import.meta.glob("./klaenge/*.mp3", { eager: true, query: "?no-inline", import: "default" }) as Record<string, string>;

function adresse(baustein: string): string | undefined {
  return klaenge[`./klaenge/${baustein}.mp3`];
}

let kontext: AudioContext | null = null;
let lautstaerke: GainNode | null = null;
const puffer = new Map<string, Promise<AudioBuffer | null>>();
const laufend = new Set<AudioScheduledSourceNode>();
let abbrechen: (() => void) | null = null;

/** In jeder Berührung aufrufen, solange Ansagen an sind: legt den Kontext an und weckt ihn wieder auf. */
export function freischalten(): void {
  try {
    if (!kontext) {
      kontext = new AudioContext();
      lautstaerke = kontext.createGain();
      lautstaerke.connect(kontext.destination);
    }
    if (kontext.state !== "running") void kontext.resume();
    // Safari: kurze Durchsage, die andere Wiedergaben leiser stellt, statt Spielklang
    const sitzung = (navigator as Navigator & { audioSession?: { type: string } }).audioSession;
    if (sitzung) sitzung.type = "transient";
  } catch {
    // ohne Web Audio bleibt es bei der Mitteilung im Untertitel
  }
}

export function bereit(): boolean {
  return kontext?.state === "running";
}

function lade(baustein: string): Promise<AudioBuffer | null> {
  let p = puffer.get(baustein);
  if (!p) {
    const url = adresse(baustein);
    p = url && kontext
      ? fetch(url).then((a) => a.arrayBuffer()).then((b) => kontext!.decodeAudioData(b)).catch(() => null)
      : Promise.resolve(null);
    puffer.set(baustein, p);
  }
  return p;
}

/** Gong vor der Ansage: zwei weiche Töne, ab Stufe 3 drei höhere. Liefert das Ende. */
function gong(stufe: number, ab: number): number {
  const ctx = kontext!;
  const toene = stufe >= 3 ? [784, 988, 1175] : [659, 880];
  let t = ab;
  for (const frequenz of toene) {
    const ton = ctx.createOscillator();
    const huelle = ctx.createGain();
    ton.type = "sine";
    ton.frequency.value = frequenz;
    huelle.gain.setValueAtTime(0, t);
    huelle.gain.linearRampToValueAtTime(0.1, t + 0.015); // leise: der Gong kündigt an, die Stimme trägt
    huelle.gain.exponentialRampToValueAtTime(0.001, t + 0.55);
    ton.connect(huelle).connect(lautstaerke!);
    ton.start(t);
    ton.stop(t + 0.6);
    laufend.add(ton);
    ton.onended = () => laufend.delete(ton);
    t += 0.18;
  }
  return t + 0.42;
}

/** Eine Ansage spielen; kehrt zurück, wenn sie zu Ende ist oder angehalten wurde. Fehlende Klänge fallen aus,
 *  der Text steht ohnehin im Untertitel. */
export async function spiele(bausteine: string[], stufe: number): Promise<void> {
  if (!kontext || !lautstaerke) return;
  if (kontext.state !== "running") await kontext.resume().catch(() => undefined);
  if (kontext.state !== "running") return;
  const ctx = kontext;
  const stuecke = await Promise.all(bausteine.map(lade));
  const pause = meldekatalog.ansagen.pause_ms / 1000;
  let t = gong(stufe, ctx.currentTime + 0.05) + 0.1;
  for (const stueck of stuecke) {
    if (!stueck) continue;
    const quelle = ctx.createBufferSource();
    quelle.buffer = stueck;
    quelle.connect(lautstaerke);
    quelle.start(t);
    laufend.add(quelle);
    quelle.onended = () => laufend.delete(quelle);
    t += stueck.duration + pause;
  }
  await new Promise<void>((fertig) => {
    const uhr = setTimeout(fertig, Math.max(0, (t - ctx.currentTime) * 1000));
    abbrechen = () => {
      clearTimeout(uhr);
      fertig();
    };
  });
  abbrechen = null;
}

export function stoppe(): void {
  for (const q of laufend) {
    try {
      q.stop();
    } catch {
      // schon zu Ende
    }
  }
  laufend.clear();
  abbrechen?.();
}

/** Für die Prüfung: welche Bausteine haben keinen Klang? */
export function ohneKlang(bausteine: string[]): string[] {
  return bausteine.filter((b) => !adresse(b));
}
