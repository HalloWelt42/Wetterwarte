<script lang="ts">
  // Sonnenbogen über dem Horizont: auf, unter, jetzt in Minuten seit Mitternacht (Ortszeit).
  import { svgId } from "./geometrie";

  let {
    auf,
    unter,
    jetzt,
    beschriftung = null,
  }: { auf: number; unter: number; jetzt: number; beschriftung?: [string, string] | null } = $props();

  let b = $state(0);
  let h = $state(0);
  const id = svgId("sonne");
  const unten = $derived(beschriftung ? 18 : 4);
  const hor = $derived(h - unten - 2);
  const rx = $derived(b / 2 - 10);
  const ry = $derived(Math.max(4, Math.min(hor - 8, rx * 0.9)));
  const cx = $derived(b / 2);
  const t = $derived(Math.max(0, Math.min(1, (jetzt - auf) / Math.max(1, unter - auf))));
  const winkel = $derived(Math.PI * (1 - t));
  const sx = $derived(cx + rx * Math.cos(winkel));
  const sy = $derived(hor - ry * Math.sin(winkel));
  const tag = $derived(jetzt > auf && jetzt < unter);
  const bogen = $derived(`M${cx - rx},${hor} A${rx},${ry} 0 0 1 ${cx + rx},${hor}`);
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && rx > 0}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      <line x1="0" y1={hor} x2={b} y2={hor} style="stroke: var(--flaeche-3); stroke-width: 2" />
      <path d={bogen} style="fill: none; stroke: var(--flaeche-3); stroke-width: 2.5; stroke-dasharray: 4 5" />
      {#if tag}
        <defs><clipPath {id}><rect x="0" y="0" width={sx} height={hor} /></clipPath></defs>
        <path d={bogen} clip-path="url(#{id})" style="fill: none; stroke: var(--sonne); stroke-width: 3" />
        <circle cx={sx} cy={sy} r="8" style="fill: var(--sonne)" />
      {/if}
      {#if beschriftung}
        <text x="2" y={h - 2} text-anchor="start" class="hell">{beschriftung[0]}</text>
        <text x={b - 2} y={h - 2} text-anchor="end" class="hell">{beschriftung[1]}</text>
      {/if}
    </svg>
  {/if}
</div>
