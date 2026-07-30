<script lang="ts">
  import { meteocon } from "../../icons";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const blitze = $derived(daten.blitze);
</script>

<div class="reihe" style="gap: var(--a3)">
  <img class="mc mittel" src={meteocon("lightning-bolt")} alt="" />
  <div><span class="blitz-zahl">{blitze?.anzahl ?? 0}</span> <span class="dimm klein-txt">letzte Stunde</span></div>
</div>
{#if blitze?.liste?.length}
  <div class="blitz-liste">{#each blitze.liste as b}<div class="bz"><span>{b.zeit}</span><span>{b.distanz}</span></div>{/each}</div>
{:else}
  <div class="klein-txt dimm" style="margin-top: var(--a2)">Keine Blitze in der Nähe</div>
{/if}
