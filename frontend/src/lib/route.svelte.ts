// Einfaches, reaktives Routing zwischen den Hauptansichten.
export type Ansicht = "dashboard" | "karte" | "aufzeichnung" | "archiv";

export const route = $state<{ ansicht: Ansicht }>({ ansicht: "dashboard" });

export function gehe(ansicht: Ansicht): void {
  route.ansicht = ansicht;
}
