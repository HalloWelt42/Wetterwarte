<script lang="ts">
  import { aktuell, stunden } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import { tipp } from "../../tipp";
  import { begriffe } from "../../begriffe";
  import LinienChart from "../../LinienChart.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const jetzt = $derived(daten.basis?.aktuell ?? aktuell);
  const stundenListe = $derived(daten.basis?.stunden?.length ? daten.basis.stunden : stunden);

  // Barometer: Luftdruck-Verlauf (falls die Stundendaten Druck liefern).
  const druckPunkte = $derived(
    stundenListe.slice(0, 24).filter((s) => s.druck != null).map((s) => ({ label: s.zeit, wert: s.druck as number })),
  );
  const druckTrend = $derived.by(() => {
    const p = druckPunkte;
    if (p.length < 4) return null;
    const d = Math.round((p[3].wert - p[0].wert) * 10) / 10;
    return { delta: d, richtung: d > 0.3 ? "steigend" : d < -0.3 ? "fallend" : "gleichbleibend" };
  });
</script>

<div class="baro-wert">
  <span class="zahl">{jetzt.druck}</span><span class="dimm" use:tipp={begriffe.hpa}>hPa</span>
  {#if druckTrend}
    <span class="tendenz" style="color: {druckTrend.delta > 0.3 ? 'var(--gut)' : druckTrend.delta < -0.3 ? 'var(--gefahr)' : 'var(--text-3)'}">
      <i class="fa-solid {druckTrend.delta > 0.3 ? 'fa-arrow-trend-up' : druckTrend.delta < -0.3 ? 'fa-arrow-trend-down' : 'fa-arrow-right-long'}"></i>
      {druckTrend.delta > 0 ? "+" : ""}{druckTrend.delta} / 3 h
    </span>
  {/if}
</div>
{#if druckPunkte.length}
  <LinienChart punkte={druckPunkte} farbe="#8b5cf6" jetztIndex={0} />
{/if}
<div class="klein-txt dimm">Tendenz {druckTrend?.richtung ?? "gleichbleibend"}</div>
