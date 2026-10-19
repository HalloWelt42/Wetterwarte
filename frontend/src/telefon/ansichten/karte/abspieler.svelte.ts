// Regenradar-Abspieler: Bilder von einer Stunde zurück (gemessen) bis zur Vorhersage +2 h, Wiedergabe
// und Wahl des Zeitpunkts. Kennt die Karte nicht; welches Bild gerade gilt, meldet er über zeigeBild.

export interface Rahmen {
  id: string;
  zeit: string; // ISO mit Versatz
  offset: number; // Minuten zum neuesten gemessenen Bild ("jetzt")
  art: "gemessen" | "vorhersage";
}

export const radarUrl = (id: string): string => `/api/v1/radar/bild/${id}.png`;

const RUECKBLICK_MIN = 60; // die Zeitleiste beginnt eine Stunde vor jetzt
const TAKT_MS = 450;

export class Abspieler {
  rahmen = $state<Rahmen[]>([]);
  index = $state(0);
  spielt = $state(false);
  #takt: ReturnType<typeof setInterval> | undefined;
  #zeigeBild: (url: string) => void;

  constructor(zeigeBild: (url: string) => void) {
    this.#zeigeBild = zeigeBild;
  }

  get aktuell(): Rahmen | undefined {
    return this.rahmen[this.index];
  }

  /** Index des neuesten gemessenen Bilds ("jetzt"). */
  get jetztIndex(): number {
    const i = this.rahmen.map((r) => r.art).lastIndexOf("gemessen");
    return i >= 0 ? i : 0;
  }

  /** Neue Bildliste übernehmen. Steht der Abspieler auf jetzt und spielt nicht, folgt er dem neuen jetzt;
   *  sonst bleibt er auf demselben Bild, solange es das noch gibt. */
  uebernimm(alle: Rahmen[]): void {
    const neu = alle.filter((r) => r.offset >= -RUECKBLICK_MIN);
    if (!neu.length) return;
    const vorher = this.aktuell;
    const folgtJetzt = !vorher || (!this.spielt && this.index === this.jetztIndex);
    for (const r of neu) new Image().src = radarUrl(r.id); // vorladen, damit die Wiedergabe nicht flackert
    this.rahmen = neu;
    const gleich = vorher ? neu.findIndex((r) => r.id === vorher.id) : -1;
    this.index = folgtJetzt || gleich < 0 ? this.jetztIndex : gleich;
    if (this.aktuell?.id !== vorher?.id) this.#zeigeBild(radarUrl(this.aktuell!.id));
  }

  waehle(i: number): void {
    this.stoppe();
    this.#setze(i);
  }

  umschalten(): void {
    if (this.spielt) this.stoppe();
    else this.starte();
  }

  starte(): void {
    if (this.#takt || this.rahmen.length < 2) return;
    this.spielt = true;
    this.#takt = setInterval(() => this.#setze(this.index + 1 >= this.rahmen.length ? 0 : this.index + 1), TAKT_MS);
  }

  stoppe(): void {
    clearInterval(this.#takt);
    this.#takt = undefined;
    this.spielt = false;
  }

  #setze(i: number): void {
    const r = this.rahmen[i];
    if (!r || i === this.index) return;
    this.index = i;
    this.#zeigeBild(radarUrl(r.id));
  }
}
