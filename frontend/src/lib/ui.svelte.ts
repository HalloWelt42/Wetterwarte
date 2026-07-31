// Zustand der Overlays (Modals, Panels, Schwebefenster).
export const ui = $state<{
  katalog: boolean;
  hilfe: boolean;
  layouts: boolean;
  ortssuche: boolean;
  einstellungen: boolean; // Einstellungs-Modal offen (welche Kachel steht in kachelConf)
  dienste: boolean; // System- & Dienste-Uebersicht
}>({
  katalog: false,
  hilfe: false,
  layouts: false,
  ortssuche: false,
  einstellungen: false,
  dienste: false,
});
