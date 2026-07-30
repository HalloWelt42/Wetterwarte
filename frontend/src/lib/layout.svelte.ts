// Gemeinsamer Zustand der benannten Layouts.
import { hole, sende } from "./api";

export interface Layout {
  id: string;
  name: string;
  ist_standard: boolean;
  daten: { id: string; typ?: string; x: number; y: number; w: number; h: number }[];
}

export const layoutState = $state<{ liste: Layout[]; aktivId: string | null }>({
  liste: [],
  aktivId: null,
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
  try {
    await sende("/layouts", "POST", { name: `${quelle.name} Kopie`, daten: quelle.daten });
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

export async function setzeStandard(id: string): Promise<void> {
  try {
    await sende(`/layouts/${id}`, "PUT", { ist_standard: true });
    await ladeLayouts();
  } catch {
    // still ignorieren
  }
}
