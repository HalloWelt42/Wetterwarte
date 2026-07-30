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
