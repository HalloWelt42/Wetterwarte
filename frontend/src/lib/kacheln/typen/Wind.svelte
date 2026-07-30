<script lang="ts">
  import { aktuell } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import { tipp } from "../../tipp";
  import { begriffe } from "../../begriffe";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const jetzt = $derived(daten.basis?.aktuell ?? aktuell);
</script>

<div class="gauge-zeile">
  <svg class="kompass" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="44" style="fill: none; stroke: var(--rand); stroke-width: 2" />
    <g style="stroke: var(--rand-stark); stroke-width: 2">
      <line x1="50" y1="7" x2="50" y2="15" /><line x1="93" y1="50" x2="85" y2="50" /><line x1="50" y1="93" x2="50" y2="85" /><line x1="7" y1="50" x2="15" y2="50" />
    </g>
    <text x="50" y="22" text-anchor="middle" style="fill: var(--text-3); font-size: 9px">N</text>
    <g transform="rotate({(jetzt.windGrad ?? 315) - 315} 50 50)">
      <line x1="50" y1="50" x2="32" y2="32" style="stroke: var(--akzent); stroke-width: 3; stroke-linecap: round" />
      <polygon points="32,32 43,34 34,43" style="fill: var(--akzent)" />
    </g>
    <circle cx="50" cy="50" r="4" style="fill: var(--akzent)" />
  </svg>
  <div class="spalte">
    <div><span class="temp temp-mittel">{jetzt.wind}</span> <span class="dimm">km/h</span></div>
    <div class="klein-txt"><span use:tipp={begriffe.boeen}>Böen</span> <b class="tnum">{jetzt.boeen} km/h</b></div>
    <div class="klein-txt dimm">aus {jetzt.windRichtung}</div>
  </div>
</div>
