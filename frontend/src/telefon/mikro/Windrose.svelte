<script lang="ts">
  // Windrose: Kreis mit Teilung, Pfeil zeigt, wohin der Wind weht (grad = woher, 0 = Nord).
  let { grad }: { grad: number } = $props();

  let b = $state(0);
  let h = $state(0);
  const r = $derived(Math.min(b, h) / 2 - 3);
  const cx = $derived(b / 2);
  const cy = $derived(h / 2);
  const lang = $derived(r * 0.78);
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && r > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <circle {cx} {cy} {r} style="fill: none; stroke: var(--flaeche-3); stroke-width: 2" />
      {#each Array.from({ length: 12 }, (_, i) => i) as i}
        {@const a = (i * 30 * Math.PI) / 180}
        {@const l = i % 3 === 0 ? 8 : 4}
        <line
          x1={cx + Math.sin(a) * r}
          y1={cy - Math.cos(a) * r}
          x2={cx + Math.sin(a) * (r - l)}
          y2={cy - Math.cos(a) * (r - l)}
          style="stroke: var({i % 3 === 0 ? '--text-3' : '--flaeche-3'}); stroke-width: 2"
        />
      {/each}
      {#if r > 40}<text x={cx} y={cy - r + 22} text-anchor="middle" class="hell">N</text>{/if}
      <g transform="rotate({grad + 180} {cx} {cy})">
        <line x1={cx} y1={cy + lang * 0.7} x2={cx} y2={cy - lang + 10} style="stroke: var(--text); stroke-width: 3.2; stroke-linecap: round" />
        <path d="M{cx - 8},{cy - lang + 14} L{cx},{cy - lang} L{cx + 8},{cy - lang + 14} Z" style="fill: var(--text)" />
      </g>
    </svg>
  {/if}
</div>
