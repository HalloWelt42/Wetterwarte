<script lang="ts">
  // Bogen über 270 Grad in fünf Stufenfarben mit Marke beim Wert (UV-Index, Luftgüte).
  let { wert, max = 11 }: { wert: number; max?: number } = $props();

  let b = $state(0);
  let h = $state(0);
  const STUFEN = ["--gut", "--w1", "--w2", "--w3", "--w4"];
  const START = 135;
  const WINKEL = 270;
  const r = $derived(Math.min(b, h * 1.18) / 2 - 7);
  const cx = $derived(b / 2);
  const cy = $derived(r + 6);
  const punkt = (grad: number) => [cx + r * Math.cos((grad * Math.PI) / 180), cy + r * Math.sin((grad * Math.PI) / 180)];
  const marke = $derived(punkt(START + (Math.min(Math.max(wert, 0), max) / max) * WINKEL));
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && r > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      {#each STUFEN as v, i}
        {@const a = punkt(START + (i * WINKEL) / STUFEN.length + 1.5)}
        {@const e = punkt(START + ((i + 1) * WINKEL) / STUFEN.length - 1.5)}
        <path d="M{a[0]},{a[1]} A{r},{r} 0 0 1 {e[0]},{e[1]}" style="fill: none; stroke: var({v}); stroke-width: 7; stroke-linecap: round; opacity: 0.9" />
      {/each}
      <circle cx={marke[0]} cy={marke[1]} r="7" style="fill: var(--text); stroke: var(--flaeche); stroke-width: 3" />
    </svg>
  {/if}
</div>
