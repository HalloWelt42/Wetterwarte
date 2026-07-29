// Zustand der Overlays (Modals, Panels, Schwebefenster).
export const ui = $state<{
  katalog: boolean;
  hilfe: boolean;
  layouts: boolean;
  einstellungen: string | null; // Name der Kachel, deren Einstellungen offen sind
}>({
  katalog: false,
  hilfe: false,
  layouts: false,
  einstellungen: null,
});
