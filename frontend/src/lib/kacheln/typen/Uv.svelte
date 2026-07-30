<script lang="ts">
  import { aktuell } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const jetzt = $derived(daten.basis?.aktuell ?? aktuell);
</script>

<div class="gauge-zeile">
  <div class="gauge">
    <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--t-heiss); stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.round((jetzt.uv ?? 6) / 11 * 100)} 100" />
    </svg>
    <span class="gwert" style="color: var(--t-heiss)">{jetzt.uv ?? 6}</span>
  </div>
  <div class="spalte">
    <div><b>{(jetzt.uv ?? 0) >= 6 ? "Hoch" : (jetzt.uv ?? 0) >= 3 ? "Mittel" : "Niedrig"}</b></div>
    <div class="klein-txt dimm">Schutz um die Mittagszeit</div>
  </div>
</div>
