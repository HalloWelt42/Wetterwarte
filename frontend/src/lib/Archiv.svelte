<script lang="ts">
  import { hole } from "./api";
  import LinienChart from "./LinienChart.svelte";
  import { orteState } from "./orte.svelte";
  import HilfeLink from "./HilfeLink.svelte";

  interface VarDef {
    slug: string;
    label: string;
    einheit: string;
  }
  // Aufloesung passend zum Zeitraum: kurze Zeitraeume zeigen die tatsaechliche
  // Aufzeichnungs-Kadenz (roh), laengere verdichten zu Stunden-/Tagesmitteln.
  const zeitraeume = [
    { tage: 1, label: "24 Stunden", aufloesung: "roh" },
    { tage: 7, label: "7 Tage", aufloesung: "stunde" },
    { tage: 30, label: "30 Tage", aufloesung: "tag" },
    { tage: 365, label: "Jahr", aufloesung: "tag" },
  ];

  let station = $state("");
  let variable = $state("temperatur");
  let zeit = $state(zeitraeume[1]); // Standard: 7 Tage (Stundenmittel)
  let verlauf = $state<{ tag: string; wert: number }[]>([]);
  let variablen = $state<VarDef[]>([]);

  const AUFL_LABEL: Record<string, string> = { roh: "Messpunkte", stunde: "Stundenmittel", tag: "Tagesmittel" };

  const einheit = $derived(variablen.find((v) => v.slug === variable)?.einheit ?? "");

  // Erste vorhandene Station vorwaehlen, sobald die Orte geladen sind.
  $effect(() => {
    if (!station && orteState.liste.length) station = orteState.liste[0].slug;
  });

  // Verfuegbare Variablen dynamisch aus dem Archiv des Ortes laden (alle aufgezeichneten).
  $effect(() => {
    const o = station;
    if (!o) return;
    hole<VarDef[]>(`/archiv/variablen?ort=${o}`)
      .then((liste) => {
        variablen = liste;
        if (liste.length && !liste.some((v) => v.slug === variable)) variable = liste[0].slug;
      })
      .catch(() => {
        variablen = [];
      });
  });

  async function laden(o: string, v: string, z: { tage: number; aufloesung: string }): Promise<void> {
    try {
      verlauf = await hole<{ tag: string; wert: number }[]>(
        `/archiv/verlauf?ort=${o}&variable=${v}&tage=${z.tage}&aufloesung=${z.aufloesung}`,
      );
    } catch {
      verlauf = [];
    }
  }
  $effect(() => {
    void laden(station, variable, zeit);
  });

  // Kennzahlen aus den echten Werten (das Diagramm selbst zeichnet LinienChart).
  const kennzahlen = $derived.by(() => {
    const werte = verlauf.map((p) => p.wert);
    if (!werte.length) return { lo: 0, hi: 0, mittel: 0 };
    return {
      lo: Math.min(...werte),
      hi: Math.max(...werte),
      mittel: werte.reduce((a, b) => a + b, 0) / werte.length,
    };
  });

  // Label je nach Aufloesung: roh -> Uhrzeit, stunde -> Tag+Stunde, tag -> Datum.
  function label(iso: string): string {
    if (!iso) return "";
    if (zeit.aufloesung === "roh") return iso.slice(11, 16); // HH:MM
    if (zeit.aufloesung === "stunde") return `${iso.slice(8, 10)}.${iso.slice(5, 7)}. ${iso.slice(11, 13)}h`;
    return `${iso.slice(8, 10)}.${iso.slice(5, 7)}.`; // DD.MM.
  }
  const rund = (x: number) => Math.round(x * 10) / 10;

  // Punkte fuer den wiederverwendbaren LinienChart (gleiche Optik wie im Dashboard).
  const archivPunkte = $derived(verlauf.map((p) => ({ label: label(p.tag), wert: p.wert })));
  const xSchritt = $derived(Math.max(1, Math.ceil(verlauf.length / 6)));
</script>

<section class="inhalt">
  <div class="seite">
    <h1>Archiv und Analyse <HilfeLink topic="archiv" /></h1>
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
          <button class:aktiv={zeit.tage === z.tage} onclick={() => (zeit = z)}>{z.label}</button>
        {/each}
      </span>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-chart-line"></i> Verlauf</h2>
      <p class="unter">{AUFL_LABEL[zeit.aufloesung]} &middot; {verlauf.length} Werte aus dem Archiv</p>
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
      <p class="unter">Berechnet aus den aufgezeichneten Werten im Zeitraum</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--a3)">
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-mild" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(kennzahlen.mittel)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Mittelwert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-heiss" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(kennzahlen.hi)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Hoechster Wert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum t-kalt" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{rund(kennzahlen.lo)}{einheit}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Tiefster Wert</div>
        </div>
        <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
          <div class="tnum" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{verlauf.length}</div>
          <div class="klein-txt dimm" style="margin-top: 4px">Messpunkte</div>
        </div>
      </div>
    </div>
  </div>
</section>
