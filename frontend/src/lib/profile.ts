// Profil-spezifische Standard-Anordnungen: jedes benannte Layout startet mit einer
// zum Zweck passenden Kachel-Auswahl, damit sich die Profile klar unterscheiden.
// Ein leeres Layout uebernimmt automatisch das Profil zu seinem Namen; ueber die
// Verwaltung laesst sich ein Layout jederzeit auf seinen Profil-Standard zuruecksetzen.
import { registry, standardKacheln } from "./kacheln/registry";

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

export interface KachelDaten {
  id: string;
  typ: string;
  x: number;
  y: number;
  w: number;
  h: number;
  conf: Record<string, unknown>;
}

// Profil-Kacheln mit einfacher Auto-Anordnung (links nach rechts, Umbruch bei 12
// Spalten). Liefert konkrete Positionen, damit die Vorschau sofort etwas zeigt.
export function profilDaten(name: string): KachelDaten[] {
  let x = 0;
  let y = 0;
  let zeilenhoehe = 0;
  return profilTypen(name).map((typ) => {
    const def = registry[typ];
    if (x + def.w > 12) {
      x = 0;
      y += zeilenhoehe;
      zeilenhoehe = 0;
    }
    const d: KachelDaten = { id: `${typ}-${x}-${y}`, typ, x, y, w: def.w, h: def.h, conf: {} };
    x += def.w;
    zeilenhoehe = Math.max(zeilenhoehe, def.h);
    return d;
  });
}
