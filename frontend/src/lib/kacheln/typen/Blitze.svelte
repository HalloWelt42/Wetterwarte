<script lang="ts">
  import { meteocon } from "../../../kern/icons";
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const blitze = $derived(daten.blitze!);
</script>

<div class="reihe" style="gap: var(--a3)">
  <img class="mc mittel" src={meteocon("lightning-bolt")} alt="" />
  <div><span class="blitz-zahl">{blitze.anzahl}</span> <span class="dimm klein-txt">letzte Stunde</span></div>
</div>
{#if blitze?.liste?.length}
  <div class="blitz-liste">{#each blitze.liste as b}<div class="bz"><span>{b.zeit}</span><span>{b.distanz}</span></div>{/each}</div>
{:else}
  <div class="klein-txt dimm" style="margin-top: var(--a2)">Keine Blitze in der Nähe</div>
{/if}
