// Zustand der Overlays (Modals, Panels, Schwebefenster).
export const ui = $state<{
  katalog: boolean;
  hilfe: boolean;
  layouts: boolean;
  ortssuche: boolean;
  einstellungen: boolean; // Einstellungs-Modal offen (welche Kachel steht in kachelConf)
  dienste: boolean; // System- & Dienste-Uebersicht
  demoOrte: boolean; // Demo-Orte-Auswahl (Extremwetter + bekannte Orte)
  spende: boolean; // Spende-/Unterstuetzen-Overlay
  willkommen: boolean; // Onboarding-/Rettungsring-Overlay fuer Erstnutzer
  menu: boolean; // mobile Navigations-Schublade (Drawer)
}>({
  katalog: false,
  hilfe: false,
  layouts: false,
  ortssuche: false,
  einstellungen: false,
  dienste: false,
  demoOrte: false,
  spende: false,
  willkommen: false,
  menu: false,
});
