<script lang="ts">
  // Blitze in Entfernungsringen um den Ort: punkte mit km und Peilung (Grad), neueste zuerst.
  let {
    punkte,
    max = 50,
    ringe = [10, 25, 50],
  }: { punkte: { km: number; grad: number }[]; max?: number; ringe?: number[] } = $props();

  let b = $state(0);
  let h = $state(0);
  const r = $derived(Math.min(b, h) / 2 - 2);
  const cx = $derived(b / 2);
  const cy = $derived(h / 2);
  const sichtbar = $derived(punkte.filter((p) => p.km <= max));
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && r > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      {#each ringe as km}
        <circle {cx} {cy} r={(km / max) * r} style="fill: none; stroke: var(--flaeche-3); stroke-width: 1.5" />
        {#if r > 50}<text x={cx + 4} y={cy - (km / max) * r + 14} text-anchor="start">{km}</text>{/if}
      {/each}
      <circle {cx} {cy} r="4" style="fill: var(--akzent)" />
      {#each sichtbar as p, i}
        {@const a = (p.grad * Math.PI) / 180}
        {@const d = (p.km / max) * r}
        <circle cx={cx + Math.sin(a) * d} cy={cy - Math.cos(a) * d} r={i < 3 ? 4.5 : 3} style="fill: var(--w1); opacity: {i < 3 ? 1 : 0.6}" />
      {/each}
    </svg>
  {/if}
</div>
