<script lang="ts">
  // Jahresmesswerte: echte, aus dem Archiv aggregierte Monatswerte eines Ortes fuer
  // ein Jahr. Zwischen den Jahren blaetterbar; das aktuelle Jahr ist markiert, ebenso
  // der laufende Monat. Hover zeigt den Detailwert als Bubble an der Position.
  import { hole } from "../../api";
  import { uhr } from "../../uhr.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  interface MonatWert {
    monat: number;
    kurz: string;
    mittel: number | null;
    minimum: number | null;
    maximum: number | null;
    summe: number | null;
    anzahl: number;
  }

  // Wie eine Variable dargestellt wird (Einheit, Farbe, Linie vs. Balken).
  const VARIABLEN: Record<string, { label: string; einheit: string; farbe: string; art: "linie" | "balken" }> = {
    temperatur: { label: "Temperatur", einheit: "°C", farbe: "#f59e0b", art: "linie" },
    feuchte: { label: "Luftfeuchte", einheit: "%", farbe: "#38bdf8", art: "linie" },
    wind: { label: "Wind", einheit: "km/h", farbe: "#34d399", art: "linie" },
    druck: { label: "Luftdruck", einheit: "hPa", farbe: "#a78bfa", art: "linie" },
    aqi: { label: "Luftgüte", einheit: "", farbe: "#fb7185", art: "balken" },
    pm2_5: { label: "Feinstaub PM2,5", einheit: "µg/m³", farbe: "#fb923c", art: "balken" },
    pm10: { label: "Feinstaub PM10", einheit: "µg/m³", farbe: "#f97316", art: "balken" },
    o3: { label: "Ozon", einheit: "µg/m³", farbe: "#60a5fa", art: "balken" },
    no2: { label: "Stickstoffdioxid", einheit: "µg/m³", farbe: "#c084fc", art: "balken" },
  };

  const variable = $derived((conf.variable as string) || "temperatur");
  const meta = $derived(VARIABLEN[variable] ?? VARIABLEN.temperatur);

  let jahre = $state<number[]>([]);
  let aktuellesJahr = $state<number>(uhr.jetzt.getFullYear());
  let jahr = $state<number | null>(null);
  let monate = $state<MonatWert[]>([]);
  let laedt = $state(true);
  let fehler = $state(false);
  let hover = $state<number | null>(null);

  // Verfuegbare Jahre laden (async .then bildet keine Reaktiv-Abhaengigkeit -> nur ort als Dep).
  $effect(() => {
    const o = ort;
    if (!o) return;
    // Ortswechsel: alten Zustand synchron verwerfen, damit der Monatswerte-Effekt nicht
    // mit dem Jahr des vorigen Ortes feuert und kein stale Hover-Index stehen bleibt.
    jahr = null;
    monate = [];
    hover = null;
    laedt = true;
    fehler = false;
    hole<{ jahre: number[]; variablen: string[]; aktuelles_jahr: number }>(`/wetter/messjahre/${o}`)
      .then((r) => {
        jahre = r.jahre;
        aktuellesJahr = r.aktuelles_jahr;
        if (jahr === null || !jahre.includes(jahr)) {
          jahr = jahre.includes(aktuellesJahr) ? aktuellesJahr : (jahre.at(-1) ?? aktuellesJahr);
        }
      })
      .catch(() => {});
  });

  // Monatswerte fuer das gewaehlte Jahr + Variable laden.
  $effect(() => {
    const o = ort;
    const j = jahr;
    const v = variable;
    if (!o || j === null) return;
    laedt = true;
    fehler = false;
    hole<{ jahr: number; aktuelles_jahr: number; monate: MonatWert[] }>(`/wetter/jahresmesswerte/${o}?jahr=${j}&variable=${v}`)
      .then((d) => {
        monate = d.monate;
        aktuellesJahr = d.aktuelles_jahr;
        laedt = false;
      })
      .catch(() => {
        fehler = true;
        laedt = false;
      });
  });

  const minJahr = $derived(jahre.length ? Math.min(jahre[0], aktuellesJahr) : aktuellesJahr);
  const maxJahr = $derived(jahre.length ? Math.max(jahre[jahre.length - 1], aktuellesJahr) : aktuellesJahr);
  const kannZurueck = $derived(jahr !== null && jahr > minJahr);
  const kannVor = $derived(jahr !== null && jahr < maxJahr);
  const istAktuellesJahr = $derived(jahr === aktuellesJahr);
  const aktMonat = $derived(istAktuellesJahr ? uhr.jetzt.getMonth() + 1 : 0);

  function blaettern(d: number) {
    if (jahr === null) return;
    const ziel = jahr + d;
    if (ziel >= minJahr && ziel <= maxJahr) jahr = ziel;
  }

  const mitWert = $derived(monate.filter((m) => m.mittel !== null));
  const hatDaten = $derived(mitWert.length > 0);

  // Wertebereich: Linien nutzen min/max der Spanne, Balken starten bei 0.
  const werteAlle = $derived(
    meta.art === "linie"
      ? mitWert.flatMap((m) => [m.minimum ?? m.mittel ?? 0, m.maximum ?? m.mittel ?? 0])
      : mitWert.map((m) => m.mittel ?? 0),
  );
  const vMin = $derived(meta.art === "balken" ? 0 : werteAlle.length ? Math.floor(Math.min(...werteAlle) / 5) * 5 : 0);
  const vMax = $derived(werteAlle.length ? Math.ceil(Math.max(...werteAlle, vMin + 1) / 5) * 5 : 10);

  // SVG-Geometrie (undistorted; meet).
  const VBW = 320;
  const BX = 30;
  const RX = 308;
  const OY = 14;
  const UY = 150;
  const BREITE = RX - BX;
  const HOEHE = UY - OY;

  const tx = (monat: number) => BX + ((monat - 0.5) / 12) * BREITE;
  const ty = (wert: number) => UY - ((wert - vMin) / (vMax - vMin || 1)) * HOEHE;

  const linienPfad = $derived(
    mitWert.map((m, i) => `${i === 0 ? "M" : "L"} ${tx(m.monat).toFixed(1)} ${ty(m.mittel as number).toFixed(1)}`).join(" "),
  );
  // Flaeche zwischen Monatsminimum und -maximum (nur Linien-Variablen).
  const bandPfad = $derived.by(() => {
    const mitSpanne = mitWert.filter((m) => m.minimum !== null && m.maximum !== null);
    if (mitSpanne.length < 2) return "";
    const oben = mitSpanne.map((m, i) => `${i === 0 ? "M" : "L"} ${tx(m.monat).toFixed(1)} ${ty(m.maximum as number).toFixed(1)}`).join(" ");
    const unten = [...mitSpanne].reverse().map((m) => `L ${tx(m.monat).toFixed(1)} ${ty(m.minimum as number).toFixed(1)}`).join(" ");
    return `${oben} ${unten} Z`;
  });
  const balkenBreite = (BREITE / 12) * 0.6;

  function fmt(w: number | null): string {
    return w === null ? "-" : `${w}${meta.einheit}`;
  }
  // Bubble-Position mit Rand-Klammerung im Sichtfenster.
  const bubbleX = $derived(hover === null || !monate[hover] ? 0 : Math.min(VBW - 46, Math.max(46, tx(monate[hover].monat))));
</script>

<div class="jm-kopf">
  <div class="jm-titel klein-txt dimm">{meta.label}{meta.einheit ? ` · ${meta.einheit}` : ""}</div>
  <div class="jm-nav">
    <button class="jm-pfeil" onclick={() => blaettern(-1)} disabled={!kannZurueck} aria-label="Vorheriges Jahr">
      <i class="fa-solid fa-chevron-left"></i>
    </button>
    <span class="jm-jahr tnum">{jahr ?? "-"}</span>
    {#if istAktuellesJahr}<span class="jm-badge">aktuell</span>{/if}
    <button class="jm-pfeil" onclick={() => blaettern(1)} disabled={!kannVor} aria-label="Nächstes Jahr">
      <i class="fa-solid fa-chevron-right"></i>
    </button>
  </div>
</div>

{#if laedt && !monate.length}
  <div class="kw-leer"><i class="fa-solid fa-spinner fa-spin"></i><div>Messwerte werden geladen ...</div></div>
{:else if fehler}
  <div class="kw-leer"><i class="fa-solid fa-triangle-exclamation"></i><div>Messwerte nicht erreichbar</div></div>
{:else if !hatDaten}
  <div class="kw-leer">
    <i class="fa-solid fa-hourglass-half"></i>
    <div>Noch keine Messwerte für {jahr}</div>
    <div class="klein-txt dimm">Werte entstehen laufend aus der Aufzeichnung.</div>
  </div>
{:else}
  <svg class="jm-svg" viewBox="0 0 {VBW} 180" preserveAspectRatio="xMidYMid meet" role="img" onpointerleave={() => (hover = null)}>
    <!-- Achsen -->
    <line x1={BX} y1={UY} x2={RX} y2={UY} stroke="var(--rand-stark)" stroke-width="1" />
    <line x1={BX} y1={OY} x2={BX} y2={UY} stroke="var(--rand)" stroke-width="1" />
    {#if vMin < 0}
      <line x1={BX} y1={ty(0)} x2={RX} y2={ty(0)} stroke="var(--rand)" stroke-width="0.7" stroke-dasharray="2 3" />
    {/if}

    <!-- Markierung des aktuellen Monats -->
    {#if aktMonat}
      <line class="jm-akt-linie" x1={tx(aktMonat)} y1={OY} x2={tx(aktMonat)} y2={UY} stroke={meta.farbe} stroke-width="1" stroke-dasharray="2 2" opacity="0.5" />
    {/if}

    {#if meta.art === "balken"}
      {#each mitWert as m}
        <rect
          x={tx(m.monat) - balkenBreite / 2}
          y={ty(m.mittel as number)}
          width={balkenBreite}
          height={UY - ty(m.mittel as number)}
          rx="1.5"
          fill={meta.farbe}
          opacity={m.monat === aktMonat ? 0.95 : 0.6}
        />
      {/each}
    {:else}
      {#if bandPfad}<path d={bandPfad} fill={meta.farbe} opacity="0.13" />{/if}
      <path d={linienPfad} fill="none" stroke={meta.farbe} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      {#each mitWert as m}
        <circle cx={tx(m.monat)} cy={ty(m.mittel as number)} r={m.monat === aktMonat ? 3.4 : 2.2} fill={meta.farbe}
          stroke={m.monat === aktMonat ? "var(--flaeche)" : "none"} stroke-width={m.monat === aktMonat ? 1.4 : 0} />
      {/each}
    {/if}

    <!-- Achsenwerte -->
    <text x={BX - 3} y={ty(vMax)} text-anchor="end" dominant-baseline="middle" font-size="7" fill="var(--text-3)">{vMax}</text>
    <text x={BX - 3} y={ty(vMin)} text-anchor="end" dominant-baseline="middle" font-size="7" fill="var(--text-3)">{vMin}</text>
    {#each monate as m}
      <text x={tx(m.monat)} y={UY + 12} text-anchor="middle" font-size="7.5"
        fill={m.monat === aktMonat ? meta.farbe : "var(--text-3)"} font-weight={m.monat === aktMonat ? 600 : 400}>{m.kurz}</text>
    {/each}

    <!-- Hover: Marker + Bubble -->
    {#if hover !== null && monate[hover]}
      {@const m = monate[hover]}
      <line x1={tx(m.monat)} y1={OY} x2={tx(m.monat)} y2={UY} stroke="var(--text-3)" stroke-width="0.8" stroke-dasharray="1 2" />
      {#if m.mittel !== null}
        <circle cx={tx(m.monat)} cy={ty(m.mittel)} r="3.6" fill="none" stroke={meta.farbe} stroke-width="1.6" />
      {/if}
      <g transform="translate({bubbleX}, {OY + 2})">
        <rect x="-44" y="0" width="88" height={meta.art === "linie" && m.minimum !== null ? 34 : 22} rx="4" fill="var(--flaeche-2)" stroke="var(--rand)" stroke-width="0.8" />
        <text x="0" y="10" text-anchor="middle" font-size="8" fill="var(--text)" font-weight="600">{m.kurz} {jahr} · {fmt(m.mittel)}</text>
        {#if meta.art === "linie" && m.minimum !== null}
          <text x="0" y="21" text-anchor="middle" font-size="7" fill="var(--text-3)">Min {fmt(m.minimum)} · Max {fmt(m.maximum)}</text>
          <text x="0" y="30" text-anchor="middle" font-size="6.5" fill="var(--text-3)">{m.anzahl} Messungen</text>
        {:else if m.mittel !== null}
          <text x="0" y="18" text-anchor="middle" font-size="6.5" fill="var(--text-3)">{m.anzahl} Messungen</text>
        {/if}
      </g>
    {/if}

    <!-- Unsichtbare Hover-Zonen je Monat (robust ggü. SVG-Skalierung) -->
    {#each monate as m, i}
      <rect x={BX + (i / 12) * BREITE} y={OY} width={BREITE / 12} height={HOEHE} fill="transparent"
        onpointerenter={() => (hover = i)} role="presentation" />
    {/each}
  </svg>
{/if}
