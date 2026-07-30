<script lang="ts">
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);
</script>

<div class="nowcast-text">{daten.basis?.nowcast?.text ?? "Kein Regen in den nächsten 3 Stunden"}</div>
<div class="nowcast-balken">
  {#each daten.basis?.nowcast?.balken ?? [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] as h}<span class="nb" style="height: {h}%"></span>{/each}
</div>
<div class="nowcast-achse"><span>jetzt</span><span>+30</span><span>+60</span><span>+90 Min</span></div>
