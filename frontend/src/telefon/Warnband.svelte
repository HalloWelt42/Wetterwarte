<script lang="ts">
  // Warnband über dem Raster, wenn im Layout keine Warnkachel steht: oberste Warnung mit Zeit,
  // bei Ausfall der Quelle "Warnlage unbekannt" (nie stillschweigend nichts).
  import { vorZeit } from "../kern/zeit";
  import { warnZeitraum } from "./kacheln/warnzeit";
  import { uhr } from "../kern/uhr.svelte";
  import { oeffne } from "./ansicht.svelte";
  import type { Kompakt } from "./typen";

  let { daten }: { daten: Kompakt } = $props();

  const status = $derived(daten.bereiche.warnungen.status);
  const liste = $derived(daten.warnungen ?? []);
  const oberste = $derived(liste[0]);
  const zone = $derived(daten.ort.zeitzone);
  const zeit = $derived(oberste ? warnZeitraum(oberste.von, oberste.bis, uhr.jetzt, zone) : "");
</script>

{#if status === "fehlt"}
  <div class="warnband unbekannt" role="status">
    <span class="stufe-marke"><i class="fa-solid fa-question"></i></span>
    <div class="wb-txt">
      <div class="wb-titel">Warnlage unbekannt</div>
      <div class="wb-zeit">Quelle antwortet nicht{daten.bereiche.warnungen.stand ? `, zuletzt ${vorZeit(daten.bereiche.warnungen.stand, uhr.jetzt)}` : ""}</div>
    </div>
  </div>
{:else if oberste}
  <button class="warnband stufe-{oberste.stufe}" onclick={() => oeffne({ art: "warnungen" })}>
    <span class="stufe-marke">{oberste.stufe}</span>
    <div class="wb-txt">
      <div class="wb-titel">{oberste.ereignis}</div>
      <div class="wb-zeit">{zeit}</div>
    </div>
    {#if liste.length > 1}<span class="wb-mehr">+{liste.length - 1} weitere</span>{/if}
  </button>
{/if}

<style>
  button.warnband {
    width: calc(100% - 2 * var(--rand));
    text-align: left;
  }
</style>
