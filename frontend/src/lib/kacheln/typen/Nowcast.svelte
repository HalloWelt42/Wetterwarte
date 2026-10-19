<script lang="ts">
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const nowcast = $derived(daten.basis!.nowcast);
  const balken = $derived(nowcast?.balken ?? []);
  const n = $derived(balken.length);
  let hoverI = $state<number | null>(null);

  // Zeitversatz eines Balkens: je Balken eine Viertelstunde ab jetzt.
  const versatz = (i: number) => i * 15;
  // Tooltip-Position in Prozent, an den Raendern eingeklemmt (nicht abschneiden).
  const tipLinks = $derived(hoverI === null ? 50 : Math.min(85, Math.max(15, ((hoverI + 0.5) / n) * 100)));
</script>

<div class="nowcast-text">{nowcast?.text ?? "Für diesen Ort gibt es keine Kurzfristvorhersage."}</div>
{#if balken.length}
<div class="nowcast-balken" role="group" aria-label="Regenintensität der nächsten 3 Stunden" onpointerleave={() => (hoverI = null)}>
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
<div class="nowcast-achse"><span>jetzt</span><span>+1 h</span><span>+2 h</span><span>+3 h</span></div>
{/if}
