// Hilfe-Store - steuert das freischwebende Hilfe-Panel (Singleton fuer die ganze App).
//
// Haelt Position, Groesse und Zustand (offen, minimiert, maximiert) sowie das aktuelle
// Thema und die In-Panel-Suche. Lage/Groesse/Zustand werden in localStorage gemerkt.
// Jeder Hilfepunkt (HilfeLink) steuert dasselbe Panel.
//
// Volltextsuche kennt zwei Bereiche: "topic" nur im gezeigten Thema, "global" ueber alle.
// Portiert aus der Vorlage hilfe-fenster-demo (HalloWelt42), an Wetterwarte angepasst.
import { listeThemen, zaehleTreffer } from "./hilfeThemen";

const KEY = "wetterwarte.hilfe";

interface Treffer {
  topicKey: string;
  local: number;
}

const STANDARD = { x: 0, y: 0, width: 460, height: 500, minimized: false, maximized: false, topic: null as string | null };

function laden(): typeof STANDARD {
  if (typeof localStorage === "undefined") return { ...STANDARD };
  try {
    const roh = localStorage.getItem(KEY);
    if (!roh) return { ...STANDARD };
    return { ...STANDARD, ...JSON.parse(roh) };
  } catch {
    return { ...STANDARD };
  }
}

class HilfeStore {
  open = $state(false);
  topicKey = $state<string | null>(null);
  query = $state("");
  scope = $state<"global" | "topic">("global");
  matchIndex = $state(0);
  matchTotal = $state(0);
  matches = $state<Treffer[]>([]);
  x = $state(STANDARD.x);
  y = $state(STANDARD.y);
  width = $state(STANDARD.width);
  height = $state(STANDARD.height);
  minimized = $state(false);
  maximized = $state(false);
  initialisiert = $state(false);

  init(): void {
    if (this.initialisiert) return;
    const p = laden();
    if (p.x === 0 && p.y === 0 && typeof window !== "undefined") {
      p.x = Math.max(20, window.innerWidth - p.width - 32);
      p.y = Math.max(20, window.innerHeight - p.height - 90);
    }
    this.x = p.x;
    this.y = p.y;
    this.width = p.width;
    this.height = p.height;
    this.minimized = p.minimized;
    this.maximized = p.maximized;
    this.initialisiert = true;
  }

  show(topic: string): void {
    this.init();
    this.topicKey = topic;
    this.open = true;
    this.minimized = false;
    this.query = "";
    this.matchIndex = 0;
    this.matches = [];
    this.matchTotal = 0;
    this.save();
  }

  select(topic: string): void {
    this.topicKey = topic;
    if (this.scope === "global" && this.query.trim()) {
      const idx = this.matches.findIndex((m) => m.topicKey === topic);
      if (idx !== -1) this.matchIndex = idx;
    } else {
      this.query = "";
      this.matchIndex = 0;
      this.recompute();
    }
    this.save();
  }

  find(topic: string, needle: string): void {
    this.show(topic);
    this.scope = "topic";
    if (needle) this.query = needle;
    this.matchIndex = 0;
    this.recompute();
  }

  toggle(topic?: string): void {
    this.init();
    if (topic && (!this.open || this.topicKey !== topic)) {
      this.show(topic);
      return;
    }
    this.open = !this.open;
    if (this.open) this.minimized = false;
    this.save();
  }

  close(): void {
    this.open = false;
    this.save();
  }

  setQuery(q: string): void {
    this.query = q;
    this.matchIndex = 0;
    this.recompute();
  }

  setScope(scope: "global" | "topic"): void {
    this.scope = scope;
    this.matchIndex = 0;
    this.recompute();
  }

  recompute(): void {
    const nadel = this.query.trim();
    const treffer: Treffer[] = [];
    if (nadel) {
      if (this.scope === "global") {
        for (const t of listeThemen()) {
          const n = zaehleTreffer(t.key, nadel);
          for (let i = 0; i < n; i++) treffer.push({ topicKey: t.key, local: i });
        }
      } else if (this.topicKey) {
        const n = zaehleTreffer(this.topicKey, nadel);
        for (let i = 0; i < n; i++) treffer.push({ topicKey: this.topicKey, local: i });
      }
    }
    this.matches = treffer;
    this.matchTotal = treffer.length;
    if (this.matchIndex >= treffer.length) this.matchIndex = 0;
    this._folgeAktivem();
  }

  _folgeAktivem(): void {
    const m = this.matches[this.matchIndex];
    if (m && m.topicKey !== this.topicKey) this.topicKey = m.topicKey;
  }

  nextMatch(): void {
    if (this.matchTotal > 0) {
      this.matchIndex = (this.matchIndex + 1) % this.matchTotal;
      this._folgeAktivem();
    }
  }
  prevMatch(): void {
    if (this.matchTotal > 0) {
      this.matchIndex = (this.matchIndex - 1 + this.matchTotal) % this.matchTotal;
      this._folgeAktivem();
    }
  }

  aktivLokal(): number {
    const m = this.matches[this.matchIndex];
    if (m && m.topicKey === this.topicKey) return m.local;
    return -1;
  }

  toggleMinimized(): void {
    this.minimized = !this.minimized;
    if (this.minimized) this.maximized = false;
    this.save();
  }
  toggleMaximized(): void {
    this.maximized = !this.maximized;
    if (this.maximized) this.minimized = false;
    else this.einpassen();
    this.save();
  }

  maximieren(): void {
    this.init();
    this.open = true;
    this.minimized = false;
    this.maximized = true;
    this.save();
  }

  einpassen(): void {
    if (typeof window === "undefined") return;
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.width = Math.min(this.width, Math.max(320, w - 24));
    this.height = Math.min(this.height, Math.max(220, h - 24));
    this.x = Math.min(Math.max(0, this.x), Math.max(0, w - this.width));
    this.y = Math.min(Math.max(0, this.y), Math.max(0, h - this.height));
  }

  setPosition(x: number, y: number): void {
    this.x = x;
    this.y = y;
  }
  setSize(w: number, h: number): void {
    this.width = Math.max(340, w);
    this.height = Math.max(240, h);
  }

  save(): void {
    if (typeof localStorage === "undefined") return;
    try {
      localStorage.setItem(
        KEY,
        JSON.stringify({
          x: this.x,
          y: this.y,
          width: this.width,
          height: this.height,
          minimized: this.minimized,
          maximized: this.maximized,
          topic: this.topicKey,
        }),
      );
    } catch {
      /* Speichern ist Bequemlichkeit; Fehler duerfen die UI nie stoeren. */
    }
  }
}

export const hilfe = new HilfeStore();
