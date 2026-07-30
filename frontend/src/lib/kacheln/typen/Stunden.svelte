<script lang="ts">
  import { meteocon } from "../../icons";
  import { stunden } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  // Pro-Kachel-Einstellung (Standard 18), Fallback auf Platzhalter-Stunden.
  const stundenAnzahl = $derived((conf.anzahl as number) ?? 18);
  const stundenListe = $derived(daten.basis?.stunden?.length ? daten.basis.stunden : stunden);
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
