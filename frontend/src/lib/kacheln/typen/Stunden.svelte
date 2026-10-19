<script lang="ts">
  import { meteocon } from "../../../kern/icons";
  import type { OrtDaten } from "../../ortdaten.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  // Pro-Kachel-Einstellung (Standard 18), Fallback auf Platzhalter-Stunden.
  const stundenAnzahl = $derived((conf.anzahl as number) ?? 18);
  const stundenListe = $derived(daten.basis!.stunden);
</script>

<div class="stunden">
  {#each stundenListe.slice(0, stundenAnzahl) as s}
    <div class="stunde">
      <span class="zeit">{s.zeit}</span>
      <img class="mc mittel" src={meteocon(s.icon)} alt="" />
      <span class="st-temp {s.tempKlasse}">{s.temp}&deg;</span>
      <span class="st-regen">{s.regen ? s.regen + "%" : ""}</span>
    </div>
  {/each}
</div>
