<script lang="ts">
  import { stunden } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import LinienChart from "../../LinienChart.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const stundenListe = $derived(daten.basis?.stunden?.length ? daten.basis.stunden : stunden);

  // Temperaturverlauf 24h als wiederverwendbarer LinienChart.
  const verlaufPunkte = $derived(stundenListe.slice(0, 24).map((s) => ({ label: s.zeit, wert: s.temp })));
</script>

<LinienChart punkte={verlaufPunkte} farbe="#f59e0b" einheit="&deg;" jetztIndex={0} />
