<script lang="ts">
  // Klima-Diagramm-Kachel: Monatsmittel Temperatur (Linie) + mittlerer
  // Monatsniederschlag (Balken) ueber den Referenzzeitraum. Daten kommen gespeichert
  // aus dem Backend (Open-Meteo-Archiv); pro Ort eigenstaendig.
  import { hole } from "../../api";
  import { uhr } from "../../uhr.svelte";
  import { zeitzoneFuer } from "../../orte.svelte";

  let { ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Aktueller Monat am Ort (fuer die Hervorhebung im Normal-Diagramm).
  const zone = $derived(zeitzoneFuer(ort));
  const aktMonat = $derived(
    Number(uhr.jetzt.toLocaleDateString("en-US", { month: "numeric", ...(zone ? { timeZone: zone } : {}) })),
  );
  let hover = $state<number | null>(null);

  interface Monat {
    monat: number;
    kurz: string;
    temp: number | null;
    niederschlag: number | null;
  }
  interface Klima {
    monate: Monat[];
    von: number | null;
    bis: number | null;
    jahresmittel_temp: number | null;
    jahresniederschlag: number | null;
  }

  let daten = $state<Klima | null>(null);
  let laedt = $state(true);
  let fehler = $state(false);

  $effect(() => {
    const o = ort;
    if (!o) return;
    laedt = true;
    fehler = false;
    hole<Klima>(`/wetter/klima/${o}`)
      .then((d) => {
        daten = d;
        laedt = false;
      })
      .catch(() => {
        fehler = true;
        laedt = false;
      });
  });

  const monate = $derived(daten?.monate ?? []);
  const tMin = $derived(monate.length ? Math.min(0, Math.floor(Math.min(...monate.map((m) => m.temp ?? 0)) / 5) * 5) : 0);
  const tMax = $derived(monate.length ? Math.ceil(Math.max(...monate.map((m) => m.temp ?? 0)) / 5) * 5 : 30);
  const nMax = $derived(monate.length ? Math.max(20, Math.ceil(Math.max(...monate.map((m) => m.niederschlag ?? 0)) / 20) * 20) : 100);

  // SVG-Geometrie
  const BX = 30; // linke Achse
  const RX = 306; // rechte Achse
  const OY = 12; // oben
  const UY = 150; // Grundlinie
  const BREITE = RX - BX;
  const HOEHE = UY - OY;

  function tx(i: number): number {
    return BX + ((i + 0.5) / 12) * BREITE;
  }
  function ty(temp: number): number {
    return UY - ((temp - tMin) / (tMax - tMin || 1)) * HOEHE;
  }
  function balken(n: number): number {
    return (n / (nMax || 1)) * HOEHE;
  }

  const tempPfad = $derived(
    monate
      .filter((m) => m.temp !== null)
      .map((m, i) => `${i === 0 ? "M" : "L"} ${tx(m.monat - 1).toFixed(1)} ${ty(m.temp as number).toFixed(1)}`)
      .join(" "),
  );
  const balkenBreite = $derived((BREITE / 12) * 0.62);
  // Bubble-Position im Sichtfenster halten.
  const bubbleX = $derived(hover === null || !monate[hover] ? 0 : Math.min(320 - 44, Math.max(44, tx(monate[hover].monat - 1))));
</script>

{#if laedt}
  <div class="kw-leer"><i class="fa-solid fa-spinner fa-spin"></i><div>Klimadaten werden geladen ...</div></div>
{:else if fehler || !monate.length}
  <div class="kw-leer"><i class="fa-solid fa-chart-column"></i><div>Keine Klimadaten</div></div>
{:else}
  <div class="klima-kopf klein-txt dimm">
    Klima {daten?.von}-{daten?.bis} &middot; <b class="tnum">{daten?.jahresmittel_temp}&deg;C</b> Jahresmittel &middot;
    <b class="tnum">{daten?.jahresniederschlag} mm</b>/Jahr
  </div>
  <svg class="klima-svg" viewBox="0 0 320 168" preserveAspectRatio="xMidYMid meet" role="img" onpointerleave={() => (hover = null)}>
    <!-- Achsen -->
    <line x1={BX} y1={UY} x2={RX} y2={UY} stroke="var(--rand-stark)" stroke-width="1" />
    <line x1={BX} y1={OY} x2={BX} y2={UY} stroke="var(--rand)" stroke-width="1" />
    <line x1={RX} y1={OY} x2={RX} y2={UY} stroke="var(--rand)" stroke-width="1" />
    <!-- Nulllinie Temperatur, falls im Bild -->
    {#if tMin < 0}
      <line x1={BX} y1={ty(0)} x2={RX} y2={ty(0)} stroke="var(--rand)" stroke-width="0.7" stroke-dasharray="2 3" />
    {/if}
    <!-- Markierung des aktuellen Monats -->
    {#if aktMonat >= 1 && aktMonat <= 12}
      <line x1={tx(aktMonat - 1)} y1={OY} x2={tx(aktMonat - 1)} y2={UY} stroke="#f59e0b" stroke-width="1" stroke-dasharray="2 2" opacity="0.5" />
    {/if}
    <!-- Niederschlags-Balken -->
    {#each monate as m}
      {#if m.niederschlag !== null}
        <rect
          x={tx(m.monat - 1) - balkenBreite / 2}
          y={UY - balken(m.niederschlag)}
          width={balkenBreite}
          height={balken(m.niederschlag)}
          rx="1.5"
          fill="var(--t-frost)"
          opacity="0.55"
        />
      {/if}
    {/each}
    <!-- Temperatur-Linie -->
    <path d={tempPfad} fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    {#each monate as m}
      {#if m.temp !== null}
        <circle cx={tx(m.monat - 1)} cy={ty(m.temp)} r="2.2" fill="#f59e0b" />
      {/if}
    {/each}
    <!-- Achsenbeschriftung -->
    <text x={BX - 3} y={ty(tMax)} text-anchor="end" dominant-baseline="middle" font-size="7" fill="var(--text-3)">{tMax}&deg;</text>
    <text x={BX - 3} y={ty(tMin)} text-anchor="end" dominant-baseline="middle" font-size="7" fill="var(--text-3)">{tMin}&deg;</text>
    <text x={RX + 3} y={OY + 4} text-anchor="start" font-size="7" fill="var(--text-3)">{nMax}</text>
    <text x={RX + 3} y={UY} text-anchor="start" dominant-baseline="middle" font-size="7" fill="var(--text-3)">mm</text>
    {#each monate as m}
      <text x={tx(m.monat - 1)} y={UY + 12} text-anchor="middle" font-size="7.5"
        fill={m.monat === aktMonat ? "#f59e0b" : "var(--text-3)"} font-weight={m.monat === aktMonat ? 600 : 400}>{m.kurz}</text>
    {/each}

    <!-- Hover: Marker + Bubble (Temperatur + Niederschlag) -->
    {#if hover !== null && monate[hover]}
      {@const m = monate[hover]}
      <line x1={tx(m.monat - 1)} y1={OY} x2={tx(m.monat - 1)} y2={UY} stroke="var(--text-3)" stroke-width="0.8" stroke-dasharray="1 2" />
      {#if m.temp !== null}
        <circle cx={tx(m.monat - 1)} cy={ty(m.temp)} r="3.4" fill="none" stroke="#f59e0b" stroke-width="1.6" />
      {/if}
      <g transform="translate({bubbleX}, {OY + 2})" pointer-events="none">
        <rect x="-42" y="0" width="84" height="30" rx="4" fill="var(--flaeche-2)" stroke="var(--rand)" stroke-width="0.8" />
        <text x="0" y="11" text-anchor="middle" font-size="8" fill="var(--text)" font-weight="600">{m.kurz}{m.monat === aktMonat ? " · jetzt" : ""}</text>
        <text x="0" y="21" text-anchor="middle" font-size="7.5" fill="var(--text-3)">
          {m.temp !== null ? `${m.temp}°C` : "-"} · {m.niederschlag !== null ? `${m.niederschlag} mm` : "-"}
        </text>
      </g>
    {/if}

    <!-- Unsichtbare Hover-Zonen je Monat -->
    {#each monate as m, i}
      <rect x={BX + (i / 12) * BREITE} y={OY} width={BREITE / 12} height={UY - OY} fill="transparent"
        onpointerenter={() => (hover = i)} role="presentation" />
    {/each}
  </svg>
{/if}
