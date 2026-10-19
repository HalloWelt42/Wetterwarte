<script lang="ts">
  import type { OrtDaten } from "../../ortdaten.svelte";
  import LinienChart from "../../LinienChart.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const stundenListe = $derived(daten.basis!.stunden);

  // Temperaturverlauf 24h als wiederverwendbarer LinienChart.
  const verlaufPunkte = $derived(stundenListe.slice(0, 24).map((s) => ({ label: s.zeit, wert: s.temp })));
</script>

<LinienChart punkte={verlaufPunkte} farbe="#f59e0b" einheit="&deg;" jetztIndex={0} />
