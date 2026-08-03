// Gemeinsamer Zustand der benannten Layouts.
import { hole, sende } from "./api";
import { profilDaten } from "./profile";

export interface Layout {
  id: string;
  name: string;
  ist_standard: boolean;
  icon?: string; // frei gewaehltes Profil-Icon (fa-Klasse); leer = Standard nach Name
  daten: { id: string; typ?: string; x: number; y: number; w: number; h: number }[];
}

export const layoutState = $state<{ liste: Layout[]; aktivId: string | null; stand: number }>({
  liste: [],
  aktivId: null,
  stand: 0, // Nonce: erzwingt ein Neuladen des Bretts (z.B. nach Profil-Zuruecksetzen)
});

export async function ladeLayouts(): Promise<void> {
  try {
    const liste = await hole<Layout[]>("/layouts");
    layoutState.liste = liste;
    if (!layoutState.aktivId) {
      const standard = liste.find((l) => l.ist_standard) ?? liste[0];
      layoutState.aktivId = standard?.id ?? null;
    }
  } catch {
    // Backend nicht erreichbar - ohne Layouts bleibt die Platzhalter-Anordnung.
  }
}

export function setzeAktiv(id: string): void {
  layoutState.aktivId = id;
}

export async function erstelleLayout(name = "Neues Layout"): Promise<Layout | null> {
  try {
    const neu = await sende<Layout>("/layouts", "POST", { name, daten: [] });
    await ladeLayouts();
    return neu;
  } catch {
    return null;
  }
}

// Kuratierter Pool an Profil-Icons (Font Awesome, themenrelevant).
export const PROFIL_ICONS: string[] = [
  "fa-house", "fa-house-chimney", "fa-building", "fa-city", "fa-warehouse",
  "fa-seedling", "fa-tree", "fa-leaf", "fa-mountain-sun", "fa-campground",
  "fa-suitcase-rolling", "fa-plane", "fa-car", "fa-sailboat", "fa-bicycle", "fa-person-hiking",
  "fa-triangle-exclamation", "fa-bolt", "fa-cloud-showers-heavy", "fa-umbrella", "fa-snowflake", "fa-wind",
  "fa-sun", "fa-cloud", "fa-temperature-half", "fa-water",
  "fa-briefcase", "fa-heart", "fa-star", "fa-location-dot", "fa-map-location-dot", "fa-table-cells-large",
];

// Name-basierte Standard-Icons (Fallback, wenn kein eigenes Icon gewaehlt wurde).
const ICON_NACH_NAME: Record<string, string> = {
  Zuhause: "fa-house",
  Garten: "fa-seedling",
  Reise: "fa-suitcase-rolling",
  Unwetter: "fa-triangle-exclamation",
};

export function profilIcon(l: Layout): string {
  return l.icon || ICON_NACH_NAME[l.name] || "fa-table-cells-large";
}

export async function setzeIcon(id: string, icon: string): Promise<void> {
  const l = layoutState.liste.find((x) => x.id === id);
  if (l) l.icon = icon; // sofort im UI spiegeln
  try {
    await sende(`/layouts/${id}`, "PUT", { icon });
  } catch {
    // still ignorieren
  }
}

export async function benenneLayout(id: string, name: string): Promise<void> {
  const sauber = name.trim();
  if (!sauber) return;
  try {
    await sende(`/layouts/${id}`, "PUT", { name: sauber });
    await ladeLayouts();
  } catch {
    // still ignorieren
  }
}

export async function dupliziereLayout(id: string): Promise<void> {
  const quelle = layoutState.liste.find((l) => l.id === id);
  if (!quelle) return;
  // Kacheln mit frischen IDs kopieren, damit sich Original und Kopie nicht ueber
  // gleiche IDs koppeln (sonst wandern Groesse/Einstellungen zwischen beiden).
  const daten = quelle.daten.map((k) => ({ ...k, id: `${k.typ}-${crypto.randomUUID()}` }));
  try {
    await sende("/layouts", "POST", { name: `${quelle.name} Kopie`, daten, icon: quelle.icon ?? "" });
    await ladeLayouts();
  } catch {
    // still ignorieren
  }
}

export async function loescheLayout(id: string): Promise<void> {
  try {
    await sende(`/layouts/${id}`, "DELETE");
    if (layoutState.aktivId === id) layoutState.aktivId = null;
    await ladeLayouts();
  } catch {
    // still ignorieren
  }
}

export async function setzeAufProfil(id: string): Promise<void> {
  const l = layoutState.liste.find((x) => x.id === id);
  if (!l) return;
  const daten = profilDaten(l.name);
  try {
    await sende(`/layouts/${id}`, "PUT", { daten });
    l.daten = daten as never;
    if (layoutState.aktivId === id) layoutState.stand++; // aktives Brett neu laden
  } catch {
    // still ignorieren
  }
}

export async function setzeStandard(id: string): Promise<void> {
  try {
    await sende(`/layouts/${id}`, "PUT", { ist_standard: true });
    await ladeLayouts();
  } catch {
    // still ignorieren
  }
}
