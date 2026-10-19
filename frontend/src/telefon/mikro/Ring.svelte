<script lang="ts">
  // Vollkreis-Anteil (Luftqualität, Feuchte).
  let { wert, max = 100, farbe = "--akzent" }: { wert: number; max?: number; farbe?: string } = $props();

  let b = $state(0);
  let h = $state(0);
  const r = $derived(Math.min(b, h) / 2 - 5);
  const umfang = $derived(2 * Math.PI * r);
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && r > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <circle cx={b / 2} cy={h / 2} {r} style="fill: none; stroke: var(--flaeche-3); stroke-width: 7" />
      <circle
        cx={b / 2}
        cy={h / 2}
        {r}
        transform="rotate(-90 {b / 2} {h / 2})"
        style="fill: none; stroke: var({farbe}); stroke-width: 7; stroke-linecap: round; stroke-dasharray: {(umfang * Math.min(wert, max)) / max} {umfang}"
      />
    </svg>
  {/if}
</div>
