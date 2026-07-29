// Gemeinsamer Zustand der benannten Layouts.
import { hole } from "./api";

export interface Layout {
  id: string;
  name: string;
  ist_standard: boolean;
  daten: { id: string; x: number; y: number; w: number; h: number }[];
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
