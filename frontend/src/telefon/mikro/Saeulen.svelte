<script lang="ts">
  // Säulen ohne Achsen, optional mit Achsenbeschriftung unten. hervor: Index, der voll deckend
  // bleibt (die übrigen gedämpft); ohne hervor sind alle voll.
  let {
    werte,
    max = undefined,
    farbe = "--regen",
    hervor = undefined,
    achse = [],
  }: { werte: number[]; max?: number; farbe?: string; hervor?: number; achse?: string[] } = $props();

  let b = $state(0);
  let h = $state(0);
  const oben = $derived(Math.max(max ?? 0, ...werte, 0.0001));
  const unten = $derived(achse.length ? 16 : 0);
  const luecke = $derived(werte.length > 16 ? 2 : 3);
  const sb = $derived((b - luecke * (werte.length - 1)) / Math.max(1, werte.length));
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <rect x="0" y={h - unten - 1} width={b} height="1" style="fill: var(--flaeche-3)" />
      {#each werte as v, i}
        {@const bh = Math.max(v > 0 ? 3 : 0, (v / oben) * (h - unten - 2))}
        <rect
          x={i * (sb + luecke)}
          y={h - unten - bh}
          width={Math.max(1, sb)}
          height={bh}
          rx={Math.min(2.5, sb / 2)}
          style="fill: var({farbe}); opacity: {hervor !== undefined && hervor !== i ? 0.55 : 1}"
        />
      {/each}
      {#each achse as a, i}
        <text x={(i * b) / Math.max(1, achse.length - 1)} y={h - 2} text-anchor={i === 0 ? "start" : i === achse.length - 1 ? "end" : "middle"}>{a}</text>
      {/each}
    </svg>
  {/if}
</div>
