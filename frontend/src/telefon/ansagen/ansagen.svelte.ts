// Tonansagen bei offener App (docs/WARNUNGEN.md): im Takt der Wetterdaten fragt die App den Server, was für den
// gezeigten Ort neu zu sagen ist (eigenes Gedächtnis des Kanals "ansage" je Gerät und Ort), und spricht es mit der
// Zeit-Stimme. Mehrere Ansagen laufen nacheinander, höchste Stufe zuerst; der Text steht dabei im Untertitel.
import { sende } from "../../kern/api";
import { meldekatalog, type Meldeart } from "../../kern/gemeinsam";
import { lies, schreib } from "../../kern/speicher";
import { konto, sicheresKonto } from "../meldungen/konto.svelte";
import { TAKT_MS } from "../wetter.svelte";
import { freischalten, spiele, stoppe } from "./spieler";

export interface Ansage {
  art: Meldeart;
  schluessel: string;
  stufe: number;
  titel: string;
  text: string;
  bausteine: string[];
  entwarnung: boolean;
}

export const ansagen = $state<{ an: boolean; spricht: Ansage | null }>({
  an: lies<boolean>("telefon.ansagen", false),
  spricht: null,
});

let kette: Promise<void> = Promise.resolve();
let warteschlange = 0;

export function sprich(a: Ansage): void {
  warteschlange++;
  kette = kette.then(async () => {
    ansagen.spricht = a;
    try {
      await spiele(a.bausteine, a.stufe);
    } finally {
      ansagen.spricht = null;
      warteschlange--;
    }
  });
}

/** Laufende Ansage beenden (Tippen auf den Untertitel). */
export function verstummen(): void {
  stoppe();
}

/** Im Tippen aufrufen: schaltet den Ton frei und legt bei Bedarf das Gerät beim Server an. */
export async function ansagenSchalten(an: boolean, ort: string): Promise<void> {
  if (an) freischalten();
  else stoppe();
  ansagen.an = an;
  schreib("telefon.ansagen", an);
  if (an) {
    await sicheresKonto(ort);
    void abholen(ort);
  }
}

export function probeansage(): void {
  freischalten();
  sprich({ art: "warnung", schluessel: "probe", stufe: 1, titel: "Probeansage", text: meldekatalog.ansagen.saetze.probe, bausteine: ["probe"], entwarnung: false });
}

async function abholen(ort: string): Promise<void> {
  if (!ansagen.an || !konto.id || !ort || document.visibilityState !== "visible" || warteschlange > 0) return;
  try {
    const neu = await sende<Ansage[]>(`/geraete/${konto.id}/ansagen?ort=${encodeURIComponent(ort)}`, "POST");
    for (const a of [...neu].sort((x, y) => y.stufe - x.stufe)) sprich(a);
  } catch {
    // ohne Verbindung: beim nächsten Takt
  }
}

/** Im Takt der Wetterdaten und beim Zurückkehren abholen; jede Berührung hält den Ton bereit. */
export function verfolgeAnsagen(ort: () => string): () => void {
  const takt = setInterval(() => void abholen(ort()), TAKT_MS);
  const erst = setTimeout(() => void abholen(ort()), 4000);
  const sichtbar = () => {
    if (document.visibilityState === "visible") void abholen(ort());
  };
  const beruehrt = () => {
    if (ansagen.an) freischalten();
  };
  document.addEventListener("visibilitychange", sichtbar);
  document.addEventListener("pointerdown", beruehrt, true);
  return () => {
    clearInterval(takt);
    clearTimeout(erst);
    document.removeEventListener("visibilitychange", sichtbar);
    document.removeEventListener("pointerdown", beruehrt, true);
  };
}

/** Nach einem Ortswechsel gleich für den neuen Ort fragen. */
export function ortGewechselt(ort: string): void {
  void abholen(ort);
}
