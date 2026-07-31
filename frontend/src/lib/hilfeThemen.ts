// Themen-Lexikon der Hilfe. Inhalte liegen als Markdown in ./hilfe/*.md mit
// Frontmatter (title, subtitle, category, icon). Vite liest sie ein (import.meta.glob
// '?raw'), das Frontmatter wird geparst und der Rumpf mit marked zu HTML gerendert -
// EINE Quelle der Wahrheit, bequem als Markdown pflegbar.
//
// Sicherheit: die Markdown-Quellen sind unsere eigenen, statisch gebuendelten Dateien
// (kein Nutzerinhalt). Nur darum ist {@html} im Hilfe-Panel unbedenklich.
import { marked } from "marked";

marked.setOptions({ gfm: true, breaks: false });

export interface Thema {
  key: string;
  title: string;
  subtitle: string;
  category: string;
  icon: string;
  markdown: string;
  html: string;
}

function parseFrontmatter(source: string): { meta: Record<string, string>; body: string } {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { meta: {}, body: source };
  const meta: Record<string, string> = {};
  for (const line of match[1].split(/\r?\n/)) {
    const idx = line.indexOf(":");
    if (idx > 0) {
      const key = line.slice(0, idx).trim();
      const value = line.slice(idx + 1).trim().replace(/^["']|["']$/g, "");
      if (key) meta[key] = value;
    }
  }
  return { meta, body: match[2] };
}

const rawFiles = import.meta.glob("./hilfe/*.md", { query: "?raw", import: "default", eager: true }) as Record<string, string>;

// Feste Reihenfolge der Themen (Rest danach alphabetisch).
const REIHENFOLGE = [
  "uebersicht",
  "hilfe",
  "kacheln",
  "orte",
  "layouts",
  "themen",
  "diagramme",
  "karte",
  "zeit",
  "aufzeichnung",
  "archiv",
  "datenfrische",
  "datenquellen",
  "dienste",
];

// Reihenfolge der Bereiche im Themen-Dropdown.
const KATEGORIE_REIHENFOLGE = ["Allgemein", "Bedienung", "Ansichten", "Hintergrund"];

const themen: Record<string, Thema> = {};

for (const [path, source] of Object.entries(rawFiles)) {
  const key = path.replace(/^.*\//, "").replace(/\.md$/, "");
  const { meta, body } = parseFrontmatter(source);
  themen[key] = {
    key,
    title: meta.title ?? key,
    subtitle: meta.subtitle ?? "",
    category: meta.category ?? "Allgemein",
    icon: meta.icon ?? "fa-circle-info",
    markdown: body.trim(),
    html: marked.parse(body) as string,
  };
}

export function getThema(key: string): Thema | null {
  return themen[key] ?? null;
}

const _knotenCache: Record<string, string[]> = {};

function textknoten(key: string): string[] {
  if (_knotenCache[key]) return _knotenCache[key];
  const topic = themen[key];
  if (!topic || typeof document === "undefined") return [];
  const el = document.createElement("div");
  el.innerHTML = topic.html;
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const texte: string[] = [];
  while (walker.nextNode()) texte.push(walker.currentNode.nodeValue ?? "");
  _knotenCache[key] = texte;
  return texte;
}

export function zaehleTreffer(key: string, needle: string): number {
  const nadel = (needle || "").toLowerCase();
  if (!nadel) return 0;
  let treffer = 0;
  for (const text of textknoten(key)) {
    const low = text.toLowerCase();
    let pos = 0;
    let i: number;
    while ((i = low.indexOf(nadel, pos)) !== -1) {
      treffer++;
      pos = i + nadel.length;
    }
  }
  return treffer;
}

export function listeThemen(): Thema[] {
  return Object.values(themen).sort((a, b) => {
    const ia = REIHENFOLGE.indexOf(a.key);
    const ib = REIHENFOLGE.indexOf(b.key);
    if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    return a.title.localeCompare(b.title, "de");
  });
}

/** Themen nach Bereich gruppiert (fuer die Gliederung im Dropdown). */
export function listeGruppen(): { kategorie: string; themen: Thema[] }[] {
  const gruppen = new Map<string, Thema[]>();
  for (const t of listeThemen()) {
    const liste = gruppen.get(t.category) ?? [];
    liste.push(t);
    gruppen.set(t.category, liste);
  }
  return [...gruppen.keys()]
    .sort((a, b) => {
      const ia = KATEGORIE_REIHENFOLGE.indexOf(a);
      const ib = KATEGORIE_REIHENFOLGE.indexOf(b);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    })
    .map((kategorie) => ({ kategorie, themen: gruppen.get(kategorie) as Thema[] }));
}
