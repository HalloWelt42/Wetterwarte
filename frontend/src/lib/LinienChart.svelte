<script module lang="ts">
  // Eindeutige Gradient-Id je Instanz (mehrere Charts auf einer Seite).
  let zaehler = 0;
</script>

<script lang="ts">
  interface Punkt {
    label: string;
    wert: number;
  }

  let {
    punkte,
    farbe = "#f59e0b",
    jetztIndex = 0,
    einheit = "",
    xJeder = 6,
    nachkomma = 0,
  }: {
    punkte: Punkt[];
    farbe?: string;
    jetztIndex?: number;
    einheit?: string;
    xJeder?: number;
    nachkomma?: number;
  } = $props();

  const gid = `lc-grad-${++zaehler}`;
  let b = $state(0);
  let h = $state(0);
  let hoverI = $state<number | null>(null);
  const pad = { oben: 10, rechts: 14, unten: 20, links: 40 };

  const werte = $derived(punkte.map((p) => p.wert));
  const min = $derived(werte.length ? Math.min(...werte) : 0);
  const max = $derived(werte.length ? Math.max(...werte) : 0);
  const puffer = $derived(Math.max(nachkomma > 0 ? 0.2 : 1, (max - min) * 0.12));
  const yMin = $derived(min - puffer);
  const yMax = $derived(max + puffer);

  function cx(i: number): number {
    const n = punkte.length;
    const innen = b - pad.links - pad.rechts;
    return pad.links + (n <= 1 ? 0 : (i / (n - 1)) * innen);
  }
  function cy(w: number): number {
    const innen = h - pad.oben - pad.unten;
    const spanne = yMax - yMin || 1;
    return pad.oben + (1 - (w - yMin) / spanne) * innen;
  }
  function fmt(w: number): string {
    return nachkomma > 0 ? w.toFixed(nachkomma) : String(Math.round(w));
  }

  // Naechsten Datenpunkt zur Mausposition bestimmen (Pixel = viewBox, 1:1).
  function beiZeiger(e: PointerEvent): void {
    const n = punkte.length;
    if (!n) {
      hoverI = null;
      return;
    }
    const r = (e.currentTarget as SVGElement).getBoundingClientRect();
    const x = e.clientX - r.left;
    const innen = b - pad.links - pad.rechts;
    const anteil = innen <= 0 ? 0 : (x - pad.links) / innen;
    hoverI = Math.max(0, Math.min(n - 1, Math.round(anteil * (n - 1))));
  }

  const linie = $derived(punkte.map((p, i) => `${cx(i)},${cy(p.wert)}`).join(" "));
  const flaeche = $derived.by(() => {
    if (!punkte.length || !b) return "";
    const boden = h - pad.unten;
    const pkte = punkte.map((p, i) => `${cx(i)},${cy(p.wert)}`).join(" L ");
    return `M ${cx(0)},${boden} L ${pkte} L ${cx(punkte.length - 1)},${boden} Z`;
  });
  const yTicks = $derived([yMax, (yMin + yMax) / 2, yMin]);
  const xTicks = $derived.by(() => {
    const t: { label: string; x: number }[] = [];
    for (let i = 0; i < punkte.length; i += Math.max(1, xJeder)) {
      if (punkte[i]) t.push({ label: punkte[i].label, x: cx(i) });
    }
    return t;
  });
</script>

<div class="lc" bind:clientWidth={b} bind:clientHeight={h}>
  {#if b > 0 && punkte.length}
    <svg width={b} height={h} viewBox="0 0 {b} {h}" onpointermove={beiZeiger} onpointerleave={() => (hoverI = null)} role="img">
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color={farbe} stop-opacity="0.32" />
          <stop offset="1" stop-color={farbe} stop-opacity="0.03" />
        </linearGradient>
      </defs>
      {#each yTicks as w}
        <line x1={pad.links} y1={cy(w)} x2={b - pad.rechts} y2={cy(w)} stroke="var(--rand)" stroke-width="1" />
        <text x={pad.links - 6} y={cy(w) + 3} fill="var(--text-3)" font-size="10" text-anchor="end">{fmt(w)}{einheit}</text>
      {/each}
      <path d={flaeche} fill="url(#{gid})" />
      <polyline points={linie} fill="none" stroke={farbe} stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      {#if jetztIndex >= 0 && jetztIndex < punkte.length}
        <line x1={cx(jetztIndex)} y1={pad.oben} x2={cx(jetztIndex)} y2={h - pad.unten} stroke="var(--gut)" stroke-width="2" stroke-dasharray="4 3" />
        <circle cx={cx(jetztIndex)} cy={cy(punkte[jetztIndex].wert)} r="4" fill="var(--gut)" stroke="var(--flaeche)" stroke-width="1.5" />
      {/if}
      {#each xTicks as t}
        <text x={t.x} y={h - 6} fill="var(--text-3)" font-size="10" text-anchor="middle">{t.label}</text>
      {/each}
      {#if hoverI !== null && punkte[hoverI]}
        {@const px = cx(hoverI)}
        {@const py = cy(punkte[hoverI].wert)}
        {@const txt = `${punkte[hoverI].label} · ${fmt(punkte[hoverI].wert)}${einheit}`}
        {@const bw = Math.max(46, txt.length * 6.2 + 14)}
        {@const bx = Math.max(pad.links, Math.min(b - pad.rechts - bw, px - bw / 2))}
        {@const by = py < 30 ? py + 10 : py - 24}
        <line x1={px} y1={pad.oben} x2={px} y2={h - pad.unten} stroke="var(--text-3)" stroke-width="1" stroke-dasharray="2 2" />
        <circle cx={px} cy={py} r="4.5" fill="none" stroke={farbe} stroke-width="2" />
        <g transform="translate({bx}, {by})" pointer-events="none">
          <rect width={bw} height="18" rx="4" fill="var(--flaeche-2)" stroke="var(--rand)" stroke-width="1" />
          <text x={bw / 2} y="12.5" text-anchor="middle" font-size="10.5" fill="var(--text)" font-weight="600">{txt}</text>
        </g>
      {/if}
    </svg>
  {/if}
</div>

<style>
  .lc {
    flex: 1;
    min-height: 64px;
    width: 100%;
  }
  .lc svg {
    display: block;
    cursor: crosshair;
  }
</style>
