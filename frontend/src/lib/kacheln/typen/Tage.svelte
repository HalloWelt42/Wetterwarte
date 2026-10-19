<script lang="ts">
  import { meteocon } from "../../../kern/icons";
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  // Pro-Kachel-Einstellungen (mit sinnvollen Standardwerten, wenn nicht gesetzt).
  const tageAnzahl = $derived((conf.anzahl as number) ?? 7);

  const tageListe = $derived(daten.basis!.tage);
</script>

<div class="tage">
  {#each tageListe.slice(0, tageAnzahl) as t}
    <div class="tag">
      <span class="wtag">{t.kurz}</span>
      <img class="mc klein" src={meteocon(t.icon)} alt="" />
      <span class="temp-band"><span style="left: {t.bandLinks}%; right: {t.bandRechts}%"></span></span>
      <span class="hilo"><span class="hi">{t.hi}&deg;</span> <span class="lo">{t.lo}&deg;</span></span>
    </div>
  {/each}
</div>
