// Arbeitszustand fuer das Bearbeiten der Einstellungen einer einzelnen Kachel.
// Das Modal fuellt/aendert `werte`; `version` steigt bei jeder Aenderung, worauf
// das Brett die Einstellungen in die Kachel-Instanz uebernimmt und speichert.
export const konf = $state<{
  id: string | null;
  typ: string;
  werte: Record<string, unknown>;
  version: number;
}>({
  id: null,
  typ: "",
  werte: {},
  version: 0,
});

// Teil-Aenderung der conf einer Kachel direkt aus dem Widget (z.B. Karten-Kachel
// schaltet ein Overlay). Das Brett merged den Patch in die betroffene Instanz und
// speichert - so bleibt jede Einstellung pro Kachel-Instanz und pro Profil.
export const konfPatch = $state<{ id: string | null; patch: Record<string, unknown>; version: number }>({
  id: null,
  patch: {},
  version: 0,
});

export function patcheKachel(id: string, patch: Record<string, unknown>): void {
  konfPatch.id = id;
  konfPatch.patch = patch;
  konfPatch.version++;
}
