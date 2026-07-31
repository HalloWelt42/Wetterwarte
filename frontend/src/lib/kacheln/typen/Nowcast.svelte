<script lang="ts">
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const balken = $derived(daten.basis?.nowcast?.balken ?? [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]);
  const n = $derived(balken.length);
  let hoverI = $state<number | null>(null);

  // Zeitversatz eines Balkens (die Achse laeuft von jetzt bis +90 Minuten).
  const versatz = (i: number) => (n <= 1 ? 0 : Math.round((i / (n - 1)) * 90));
  // Tooltip-Position in Prozent, an den Raendern eingeklemmt (nicht abschneiden).
  const tipLinks = $derived(hoverI === null ? 50 : Math.min(85, Math.max(15, ((hoverI + 0.5) / n) * 100)));
</script>

<div class="nowcast-text">{daten.basis?.nowcast?.text ?? "Kein Regen in den nächsten 3 Stunden"}</div>
<div class="nowcast-balken" role="group" aria-label="Regenintensität der nächsten 90 Minuten" onpointerleave={() => (hoverI = null)}>
  {#each balken as h, i}
    <span
      class="nb"
      class:nb-jetzt={i === 0}
      class:nb-aktiv={hoverI === i}
      style="height: {h}%"
      role="presentation"
      onpointerenter={() => (hoverI = i)}
    ></span>
  {/each}
  {#if hoverI !== null}
    <div class="nowcast-tip" style="left: {tipLinks}%">
      <b>{hoverI === 0 ? "jetzt" : `+${versatz(hoverI)} Min`}</b>
      <span class="dimm">{balken[hoverI]}%</span>
    </div>
  {/if}
</div>
<div class="nowcast-achse"><span>jetzt</span><span>+30</span><span>+60</span><span>+90 Min</span></div>
