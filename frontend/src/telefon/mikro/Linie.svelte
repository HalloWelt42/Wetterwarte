<script lang="ts">
  // Verlaufslinie ohne Achsen. farbe: CSS-Variable (z. B. "--regen") oder "temp" für den
  // Verlauf nach Temperaturstufen. jetzt: Index mit Punkt (-1 = keiner, Standard: letzter).
  import { glattePfad, svgId, tempVar } from "./geometrie";

  let {
    werte,
    farbe = "--akzent",
    flaeche = false,
    jetzt = undefined,
    beschriften = 0,
    minmax = false,
    einheit = "°",
  }: {
    werte: number[];
    farbe?: string;
    flaeche?: boolean;
    jetzt?: number;
    beschriften?: number;
    minmax?: boolean;
    einheit?: string;
  } = $props();

  let b = $state(0);
  let h = $state(0);
  const id = svgId("linie");

  const lo = $derived(Math.min(...werte));
  const hi = $derived(Math.max(...werte));
  const spanne = $derived(hi - lo || 1);
  const oben = $derived(beschriften || minmax ? 18 : 5);
  const unten = $derived(minmax ? 17 : 5);
  const x = (i: number) => 5 + (i * (b - 10)) / Math.max(1, werte.length - 1);
  const y = (v: number) => oben + (1 - (v - lo) / spanne) * (h - oben - unten);
  const punkte = $derived(werte.map((v, i) => [x(i), y(v)] as [number, number]));
  const pfad = $derived(glattePfad(punkte));
  const jetztIndex = $derived(jetzt === undefined ? werte.length - 1 : jetzt);
  const strich = $derived(farbe === "temp" ? `url(#${id})` : `var(${farbe})`);
  const iHi = $derived(werte.indexOf(hi));
  const iLo = $derived(werte.indexOf(lo));
  const rund = (v: number) => String(Math.round(v));
  const klemm = (v: number) => Math.min(Math.max(v, 14), b - 14);
</script>

<div class="mikro-feld" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && h > 0 && werte.length > 1}
    <svg class="mikro" viewBox="0 0 {b} {h}" width={b} height={h} aria-hidden="true">
      {#if farbe === "temp"}
        <defs>
          <linearGradient {id} x1="0" y1={y(lo)} x2="0" y2={y(hi)} gradientUnits="userSpaceOnUse">
            {#each [0, 1, 2, 3, 4] as s}
              <stop offset={s / 4} style="stop-color: var({tempVar(lo + (s / 4) * spanne)})" />
            {/each}
          </linearGradient>
        </defs>
      {/if}
      {#if flaeche}
        <path d="{pfad} L{x(werte.length - 1)},{h} L{x(0)},{h} Z" style="fill: {farbe === 'temp' ? 'var(--t-mild)' : strich}; opacity: 0.16" />
      {/if}
      <path d={pfad} style="fill: none; stroke: {strich}; stroke-width: 2.6; stroke-linecap: round" />
      {#if beschriften}
        {#each werte as v, i}
          {#if i % beschriften === 0}<text x={x(i)} y={y(v) - 7} text-anchor="middle" class="hell">{rund(v)}{einheit}</text>{/if}
        {/each}
      {/if}
      {#if minmax}
        <text x={klemm(x(iHi))} y={y(hi) - 6} text-anchor="middle" class="hell">{rund(hi)}{einheit}</text>
        <text x={klemm(x(iLo))} y={y(lo) + 15} text-anchor="middle">{rund(lo)}{einheit}</text>
      {/if}
      {#if jetztIndex >= 0 && jetztIndex < werte.length}
        <circle cx={x(jetztIndex)} cy={y(werte[jetztIndex])} r="5" style="fill: var(--text); stroke: var(--flaeche); stroke-width: 2.5" />
      {/if}
    </svg>
  {/if}
</div>
