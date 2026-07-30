<script lang="ts">
  import { hole } from "./api";
  import LinienChart from "./LinienChart.svelte";
  import { orteState } from "./orte.svelte";

  const variablen = [
    { slug: "temperatur", label: "Temperatur", einheit: "°" },
    { slug: "wind", label: "Wind", einheit: " km/h" },
    { slug: "druck", label: "Luftdruck", einheit: " hPa" },
    { slug: "feuchte", label: "Feuchte", einheit: " %" },
  ];
  const zeitraeume = [
    { tage: 7, label: "7 Tage" },
    { tage: 30, label: "30 Tage" },
    { tage: 365, label: "Jahr" },
  ];

  let station = $state("");
  let variable = $state("temperatur");
  let tage = $state(30);
  let verlauf = $state<{ tag: string; wert: number }[]>([]);

  const einheit = $derived(variablen.find((v) => v.slug === variable)?.einheit ?? "");

  // Erste vorhandene Station vorwaehlen, sobald die Orte geladen sind.
  $effect(() => {
    if (!station && orteState.liste.length) station = orteState.liste[0].slug;
  });

  async function laden(o: string, v: string, t: number): Promise<void> {
    try {
      verlauf = await hole<{ tag: string; wert: number }[]>(`/archiv/verlauf?ort=${o}&variable=${v}&tage=${t}`);
    } catch {
      verlauf = [];
    }
  }
  $effect(() => {
    void laden(station, variable, tage);
  });

  // Diagramm-Geometrie aus den echten Werten berechnen.
  const chart = $derived.by(() => {
    const v = verlauf;
    if (v.length < 2) return { linie: "", flaeche: "", lo: 0, hi: 0, mittel: 0 };
    const werte = v.map((p) => p.wert);
    const lo = Math.min(...werte);
    const hi = Math.max(...werte);
    const spanne = Math.max(0.1, hi - lo);
    const n = v.length;
    const x = (i: number) => (i / (n - 1)) * 600;
    const y = (w: number) => 164 - ((w - lo) / spanne) * 148;
    const pts = v.map((p, i) => `${x(i).toFixed(1)},${y(p.wert).toFixed(1)}`);
    const flaeche = `M${pts.map((p, i) => (i === 0 ? p : "L" + p)).join(" ")} L600,180 L0,180 Z`;
    const mittel = werte.reduce((a, b) => a + b, 0) / n;
    return { linie: pts.join(" "), flaeche, lo, hi, mittel };
  });

  function datum(iso: string): string {
    return iso ? `${iso.slice(8, 10)}.${iso.slice(5, 7)}.` : "";
  }
  const rund = (x: number) => Math.round(x * 10) / 10;

  // Punkte fuer den wiederverwendbaren LinienChart (gleiche Optik wie im Dashboard).
  const archivPunkte = $derived(verlauf.map((p) => ({ label: datum(p.tag), wert: p.wert })));
  const xSchritt = $derived(Math.max(1, Math.ceil(verlauf.length / 6)));
</script>

<section class="inhalt">
  <div class="seite">
    <h1>Archiv und Analyse</h1>
    <p class="unter-gross">
      Langzeitdaten aus der eigenen PostgreSQL - periodisch aufgezeichnet und hier ausgewertet.
    </p>

    <div class="reihe" style="gap: var(--a3); flex-wrap: wrap; margin-bottom: var(--a4)">
      <select class="feld" style="width: auto; min-width: 230px" bind:value={station}>
        {#each orteState.liste as s}<option value={s.slug}>{s.name}</option>{/each}
      </select>
      <span class="segment">
        {#each variablen as v}
          <button class:aktiv={variable === v.slug} onclick={() => (variable = v.slug)}>{v.label}</button>
        {/each}
      </span>
      <span class="segment">
        {#each zeitraeume as z}
          <button class:aktiv={tage === z.tage} onclick={() => (tage = z.tage)}>{z.label}</button>
        {/each}
      </span>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-chart-line"></i> Verlauf</h2>
      <p class="unter">Tagesmittel &middot; {verlauf.length} Tage aus dem Archiv</p>
      {#if verlauf.length >= 2}
        <div style="height: 200px; display: flex">
          <LinienChart punkte={archivPunkte} farbe="#2f7ce0" jetztIndex={-1} xJeder={xSchritt} nachkomma={1} />
        </div>
      {:else}
        <div class="kw-leer" style="min-height: 160px"><i class="fa-solid fa-hourglass-half"></i><div>Archiv wird noch befuellt ...</div></div>
      {/if}
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-award"></i> Kennzahlen im Zeitraum</h2>
      <p class="unter">Berechnet aus den aufgezeichneten Tagesmitteln</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--a3)">
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-mild" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(chart.mittel)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Mittelwert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-heiss" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(chart.hi)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Hoechster Tageswert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-kalt" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(chart.lo)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Tiefster Tageswert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{verlauf.length}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Aufgezeichnete Tage</div>
        </div>
      </div>
    </div>
  </div>
</section>
