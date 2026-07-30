// Darstellungsmodus: dichtes Dashboard (Standard) oder atmosphaerisch mit
// Vollbild-Hintergrund je Wetterlage. Die Wahl wird gemerkt (localStorage).
import { lies, schreib } from "./speicher";

export const stil = $state<{ atmo: boolean }>({ atmo: lies("stil.atmo", false) });

// Aenderung dauerhaft merken (App-weiter Wurzel-Effekt, laeuft solange die App laeuft).
$effect.root(() => {
  $effect(() => schreib("stil.atmo", stil.atmo));
});
