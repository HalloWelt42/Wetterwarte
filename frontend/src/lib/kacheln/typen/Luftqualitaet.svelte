<script lang="ts">
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import { tipp } from "../../tipp";
  import { begriffe } from "../../begriffe";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const schadstoffe = $derived((conf.schadstoffe as string[]) ?? ["pm2_5", "pm10", "o3", "no2"]);
  const luft = $derived(daten.luft);
  const aqiVar = $derived(
    !luft ? "var(--gut)" : luft.aqi <= 40 ? "var(--gut)" : luft.aqi <= 60 ? "var(--warn)" : "var(--gefahr)",
  );
</script>

<div class="gauge-zeile">
  <div class="gauge">
    <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
      <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: {aqiVar}; stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.min(100, luft?.aqi ?? 34)} 100" />
    </svg>
    <span class="gwert" style="color: {aqiVar}">{luft?.aqi ?? 34}</span>
  </div>
  <div class="spalte">
    <div class="lq-kopf"><b class="lq-stufe">{luft?.label ?? "Gut"}</b> <span class="dimm klein-txt" use:tipp={begriffe.aqi}>EU-AQI</span></div>
    <div class="lq-gitter">
      {#if schadstoffe.includes("pm2_5")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.pm25}>PM2,5</span><span class="lq-wert">{luft?.pm2_5 ?? 8}</span></div>{/if}
      {#if schadstoffe.includes("pm10")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.pm10}>PM10</span><span class="lq-wert">{luft?.pm10 ?? 15}</span></div>{/if}
      {#if schadstoffe.includes("o3")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.ozon}>O&#8323;</span><span class="lq-wert">{luft?.o3 ?? 62}</span></div>{/if}
      {#if schadstoffe.includes("no2")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.no2}>NO&#8322;</span><span class="lq-wert">{luft?.no2 ?? 11}</span></div>{/if}
    </div>
  </div>
</div>
