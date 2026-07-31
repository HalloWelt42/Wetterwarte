// Zustand der Overlays (Modals, Panels, Schwebefenster).
export const ui = $state<{
  katalog: boolean;
  hilfe: boolean;
  layouts: boolean;
  ortssuche: boolean;
  einstellungen: boolean; // Einstellungs-Modal offen (welche Kachel steht in kachelConf)
  dienste: boolean; // System- & Dienste-Uebersicht
  demoOrte: boolean; // Demo-Orte-Auswahl (Extremwetter + bekannte Orte)
}>({
  katalog: false,
  hilfe: false,
  layouts: false,
  ortssuche: false,
  einstellungen: false,
  dienste: false,
  demoOrte: false,
});
