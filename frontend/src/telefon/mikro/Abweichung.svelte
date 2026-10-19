<script lang="ts">
  // Abweichung vom Normalwert je Spalte: wärmer nach oben, kühler nach unten. null = keine Angabe.
  let { werte, hervor = undefined, achse = [] }: { werte: (number | null)[]; hervor?: number; achse?: string[] } = $props();

  let b = $state(0);
  let h = $state(0);
  const unten = $derived(achse.length ? 16 : 0);
  const max = $derived(Math.max(0.5, ...werte.map((v) => Math.abs(v ?? 0))));
  const mitte = $derived((h - unten) / 2);
  const sb = $derived((b - 3 * (werte.length - 1)) / Math.max(1, werte.length));
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <rect x="0" y={mitte - 0.5} width={b} height="1" style="fill: var(--flaeche-3)" />
      {#each werte as v, i}
        {#if v !== null}
          {@const bh = Math.max(2, (Math.abs(v) / max) * (mitte - 2))}
          <rect
            x={i * (sb + 3)}
            y={v >= 0 ? mitte - bh : mitte}
            width={Math.max(1, sb)}
            height={bh}
            rx="2"
            style="fill: var({v >= 0 ? '--t-heiss' : '--t-frost'}); opacity: {hervor === undefined || hervor === i ? 1 : 0.5}"
          />
        {/if}
      {/each}
      {#each achse as a, i}
        <text x={(i * b) / Math.max(1, achse.length - 1)} y={h - 2} text-anchor={i === 0 ? "start" : i === achse.length - 1 ? "end" : "middle"}>{a}</text>
      {/each}
    </svg>
  {/if}
</div>
