<script lang="ts">
  import { meteocon } from "../../../kern/icons";
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const warnungenListe = $derived(daten.warnungen ?? []);
</script>

{#if warnungenListe.length}
  {#each warnungenListe as w}
    <div class="warnbanner warnstufe-{w.stufe}">
      {#if w.icon}<img class="mc mittel" src={meteocon(w.icon)} alt="" />{:else}<i class="fa-solid fa-triangle-exclamation fa-lg"></i>{/if}
      <div class="wb-txt"><div class="wb-titel">{w.titel}</div><div class="wb-zeit">{w.zeit}</div></div>
    </div>
  {/each}
{:else}
  <div class="kw-leer"><i class="fa-solid fa-shield-halved"></i><div>Keine Warnungen aktiv</div></div>
{/if}
