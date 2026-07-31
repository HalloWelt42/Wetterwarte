<script lang="ts">
  // Uhr-Kachel in mehreren Varianten (digital, analog, gross). Nutzt die globale
  // Uhr (sekuendlich). Kein Ortsbezug.
  import { uhr } from "../../uhr.svelte";

  let { conf = {} }: { conf?: Record<string, any>; ort?: string } = $props();
  const variante = $derived((conf.variante as string) ?? "digital");

  const zeit = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
  const zeitKurz = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }));
  const datum = $derived(uhr.jetzt.toLocaleDateString("de-DE", { weekday: "long", day: "2-digit", month: "long", year: "numeric" }));

  const sek = $derived(uhr.jetzt.getSeconds());
  const min = $derived(uhr.jetzt.getMinutes());
  const std = $derived(uhr.jetzt.getHours() % 12);
  const sekW = $derived(sek * 6);
  const minW = $derived(min * 6 + sek * 0.1);
  const stdW = $derived(std * 30 + min * 0.5);
</script>

{#if variante === "analog"}
  <div class="uhr-analog-wrap">
    <svg viewBox="0 0 100 100" class="uhr-analog" preserveAspectRatio="xMidYMid meet">
      <circle cx="50" cy="50" r="46" fill="none" stroke="var(--rand)" stroke-width="2" />
      {#each Array(12) as _unused, i}
        <line x1="50" y1="7" x2="50" y2="13" stroke="var(--rand-stark)" stroke-width="2" transform="rotate({i * 30} 50 50)" />
      {/each}
      <line x1="50" y1="52" x2="50" y2="29" stroke="var(--text)" stroke-width="3.2" stroke-linecap="round" transform="rotate({stdW} 50 50)" />
      <line x1="50" y1="54" x2="50" y2="18" stroke="var(--text)" stroke-width="2.2" stroke-linecap="round" transform="rotate({minW} 50 50)" />
      <line x1="50" y1="58" x2="50" y2="14" stroke="var(--akzent)" stroke-width="1.2" stroke-linecap="round" transform="rotate({sekW} 50 50)" />
      <circle cx="50" cy="50" r="2.6" fill="var(--akzent)" />
    </svg>
    <div class="uhr-datum klein-txt dimm">{datum}</div>
  </div>
{:else if variante === "gross"}
  <div class="uhr-gross">
    <div class="uhr-gross-zeit tnum">{zeitKurz}</div>
    <div class="uhr-datum dimm">{datum}</div>
  </div>
{:else}
  <div class="uhr-digital">
    <div class="uhr-zeit tnum">{zeit}</div>
    <div class="uhr-datum dimm">{datum}</div>
  </div>
{/if}
