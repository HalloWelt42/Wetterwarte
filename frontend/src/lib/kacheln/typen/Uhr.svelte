<script lang="ts">
  // Uhr-Kachel in mehreren Varianten (digital, analog, gross). Nutzt die globale
  // Uhr (sekuendlich). Kein Ortsbezug.
  import { uhr } from "../../uhr.svelte";

  let { conf = {} }: { conf?: Record<string, any>; ort?: string } = $props();
  const variante = $derived((conf.variante as string) ?? "digital");

  // Zeitzone: leer = automatisch (lokale Zone des Geraets), sonst eine echte IANA-Zone.
  const zone = $derived((conf.zeitzone as string) || "");
  const zeitOpt = $derived(zone ? { timeZone: zone } : {});
  const zoneLabel = $derived(zone ? (zone.split("/").pop() ?? zone).replace(/_/g, " ") : "");

  const zeit = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit", ...zeitOpt }));
  const zeitKurz = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", ...zeitOpt }));
  const datum = $derived(uhr.jetzt.toLocaleDateString("de-DE", { weekday: "long", day: "2-digit", month: "long", year: "numeric", ...zeitOpt }));

  // Fuer die Analoguhr die Zeit in der gewaehlten Zone als Wanduhrzeit ableiten.
  const zeitInZone = $derived(zone ? new Date(uhr.jetzt.toLocaleString("en-US", { timeZone: zone })) : uhr.jetzt);
  const sek = $derived(zeitInZone.getSeconds());
  const min = $derived(zeitInZone.getMinutes());
  const std = $derived(zeitInZone.getHours() % 12);
  const sekW = $derived(sek * 6);
  const minW = $derived(min * 6 + sek * 0.1);
  const stdW = $derived(std * 30 + min * 0.5);
</script>

{#snippet zoneMarke()}
  {#if zoneLabel}<div class="uhr-zone klein-txt dimm"><i class="fa-solid fa-earth-europe"></i> {zoneLabel}</div>{/if}
{/snippet}

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
    {@render zoneMarke()}
  </div>
{:else if variante === "gross"}
  <div class="uhr-gross">
    <div class="uhr-gross-zeit tnum">{zeitKurz}</div>
    <div class="uhr-datum dimm">{datum}</div>
    {@render zoneMarke()}
  </div>
{:else}
  <div class="uhr-digital">
    <div class="uhr-zeit tnum">{zeit}</div>
    <div class="uhr-datum dimm">{datum}</div>
    {@render zoneMarke()}
  </div>
{/if}
