<script lang="ts">
  // Schlanker Dispatcher: waehlt anhand des Typs die eigenstaendige Kachel-Komponente.
  // Jede Komponente holt ihre Daten selbst (siehe typen/*.svelte + ortdaten.svelte.ts).
  import Aktuell from "./typen/Aktuell.svelte";
  import Stunden from "./typen/Stunden.svelte";
  import Warnungen from "./typen/Warnungen.svelte";
  import Karte from "./typen/Karte.svelte";
  import Tage from "./typen/Tage.svelte";
  import Nowcast from "./typen/Nowcast.svelte";
  import Wind from "./typen/Wind.svelte";
  import Sonne from "./typen/Sonne.svelte";
  import Mond from "./typen/Mond.svelte";
  import Luftqualitaet from "./typen/Luftqualitaet.svelte";
  import Uv from "./typen/Uv.svelte";
  import Pollen from "./typen/Pollen.svelte";
  import Barometer from "./typen/Barometer.svelte";
  import Blitze from "./typen/Blitze.svelte";
  import Verlauf from "./typen/Verlauf.svelte";
  import Uhr from "./typen/Uhr.svelte";
  import Kalender from "./typen/Kalender.svelte";
  import Klima from "./typen/Klima.svelte";

  const KOMPONENTEN: Record<string, unknown> = {
    aktuell: Aktuell,
    stunden: Stunden,
    warnungen: Warnungen,
    karte: Karte,
    tage: Tage,
    nowcast: Nowcast,
    wind: Wind,
    sonne: Sonne,
    mond: Mond,
    luftqualitaet: Luftqualitaet,
    uv: Uv,
    pollen: Pollen,
    barometer: Barometer,
    blitze: Blitze,
    verlauf: Verlauf,
    uhr: Uhr,
    kalender: Kalender,
    klima: Klima,
  };

  let { typ, conf = {}, ort }: { typ: string; conf?: Record<string, any>; ort: string } = $props();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Komponente = $derived(KOMPONENTEN[typ] as any);
</script>

{#if Komponente}
  <Komponente {conf} {ort} />
{/if}
