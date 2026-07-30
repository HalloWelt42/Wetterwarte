// Profil-spezifische Standard-Anordnungen: jedes benannte Layout startet mit einer
// zum Zweck passenden Kachel-Auswahl, damit sich die Profile klar unterscheiden.
// Ein leeres Layout uebernimmt automatisch das Profil zu seinem Namen; ueber die
// Verwaltung laesst sich ein Layout jederzeit auf seinen Profil-Standard zuruecksetzen.
import { standardKacheln } from "./kacheln/registry";

const PROFILE: Record<string, string[]> = {
  // Zuhause: umfassendes Dashboard (alle Kacheln).
  Zuhause: standardKacheln,
  // Garten: was fuer Pflanzen/Draussen zaehlt.
  Garten: ["aktuell", "pollen", "uv", "nowcast", "wind", "sonne", "tage", "verlauf"],
  // Reise: kompakter Ueberblick fuer unterwegs.
  Reise: ["aktuell", "tage", "stunden", "karte", "sonne"],
  // Unwetter: alles Zeitkritische gross und zusammen.
  Unwetter: ["warnungen", "karte", "blitze", "nowcast", "wind", "aktuell"],
};

export function profilTypen(name: string): string[] {
  return PROFILE[name] ?? standardKacheln;
}
