<script lang="ts">
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const jetzt = $derived(daten.basis!.aktuell);
</script>

<div class="gauge-zeile">
  <div class="gauge">
    <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--t-heiss); stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.round(jetzt.uv / 11 * 100)} 100" />
    </svg>
    <span class="gwert" style="color: var(--t-heiss)">{jetzt.uv}</span>
  </div>
  <div class="spalte">
    <div><b>{jetzt.uv >= 6 ? "Hoch" : jetzt.uv >= 3 ? "Mittel" : "Niedrig"}</b></div>
    <div class="klein-txt dimm">Schutz um die Mittagszeit</div>
  </div>
</div>
