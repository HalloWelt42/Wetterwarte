<script lang="ts">
  // Mondscheibe: anteil 0..1 beleuchtet, zunehmend = rechte Seite hell (Nordhalbkugel).
  let { anteil, zunehmend }: { anteil: number; zunehmend: boolean } = $props();

  let b = $state(0);
  let h = $state(0);
  const r = $derived(Math.min(b, h) / 2 - 2);
  const cx = $derived(b / 2);
  const cy = $derived(h / 2);
  const e = $derived(Math.abs(1 - 2 * anteil) * r);
  const seite = $derived(zunehmend ? 1 : 0);
  const bauch = $derived(anteil > 0.5 ? seite : 1 - seite);
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && r > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <circle {cx} {cy} {r} style="fill: var(--flaeche-3)" />
      <path d="M{cx},{cy - r} A{r},{r} 0 0 {seite} {cx},{cy + r} A{e},{r} 0 0 {bauch} {cx},{cy - r} Z" style="fill: var(--text); opacity: 0.92" />
    </svg>
  {/if}
</div>
