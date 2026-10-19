<script lang="ts">
  import { DRUCK_STABIL_HPA } from "../../../kern/grenzen";
  import type { OrtDaten } from "../../ortdaten.svelte";
  import { tipp } from "../../tipp";
  import { begriffe } from "../../../kern/begriffe";
  import LinienChart from "../../LinienChart.svelte";

  // Daten kommen von der Kachelhülle (KachelKoerper), erst wenn sie geladen sind.
  let { conf = {}, ort, daten }: { conf?: Record<string, any>; ort: string; daten: OrtDaten } = $props();

  const jetzt = $derived(daten.basis!.aktuell);
  const stundenListe = $derived(daten.basis!.stunden);

  // Barometer: Luftdruck-Verlauf (falls die Stundendaten Druck liefern).
  const druckPunkte = $derived(
    stundenListe.slice(0, 24).filter((s) => s.druck != null).map((s) => ({ label: s.zeit, wert: s.druck as number })),
  );
  const druckTrend = $derived.by(() => {
    const p = druckPunkte;
    if (p.length < 4) return null;
    const d = Math.round((p[3].wert - p[0].wert) * 10) / 10;
    return { delta: d, richtung: d > DRUCK_STABIL_HPA ? "steigend" : d < -DRUCK_STABIL_HPA ? "fallend" : "gleichbleibend" };
  });
</script>

<div class="baro-wert">
  <span class="zahl">{jetzt.druck}</span><span class="dimm" use:tipp={begriffe.hpa}>hPa</span>
  {#if druckTrend}
    <span class="tendenz" style="color: {druckTrend.delta > DRUCK_STABIL_HPA ? 'var(--gut)' : druckTrend.delta < -DRUCK_STABIL_HPA ? 'var(--gefahr)' : 'var(--text-3)'}">
      <i class="fa-solid {druckTrend.delta > DRUCK_STABIL_HPA ? 'fa-arrow-trend-up' : druckTrend.delta < -DRUCK_STABIL_HPA ? 'fa-arrow-trend-down' : 'fa-arrow-right-long'}"></i>
      {druckTrend.delta > 0 ? "+" : ""}{druckTrend.delta} / 3 h
    </span>
  {/if}
</div>
{#if druckPunkte.length}
  <LinienChart punkte={druckPunkte} farbe="#8b5cf6" jetztIndex={0} />
{/if}
<div class="klein-txt dimm">Tendenz {druckTrend?.richtung ?? "gleichbleibend"}</div>
