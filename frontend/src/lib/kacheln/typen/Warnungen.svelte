<script lang="ts">
  import { meteocon } from "../../icons";
  import { warnungen } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const warnungenListe = $derived(daten.geladen ? (daten.warnungen ?? []) : warnungen);
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
