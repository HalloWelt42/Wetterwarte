<script lang="ts">
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import { uhr } from "../../uhr.svelte";
  import { zeitzoneFuer } from "../../orte.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  // Auf-/Untergang liefert das Backend als Ortszeit; darum muss auch das "Jetzt"
  // die Wanduhrzeit am Ort sein - sonst wandert der Marker bei fernen Orten falsch.
  const zone = $derived(zeitzoneFuer(ort));
  const jetztAmOrt = $derived(zone ? new Date(uhr.jetzt.toLocaleString("en-US", { timeZone: zone })) : uhr.jetzt);

  // Sonne: Bogen mit Live-Marker (Vorbild alter SunWidget).
  function zuMinuten(t?: string): number {
    const m = t ? /^(\d{1,2}):(\d{2})/.exec(t) : null;
    return m ? +m[1] * 60 + +m[2] : 0;
  }
  const sonneAuf = $derived(zuMinuten(daten.basis?.sonne?.aufgang));
  const sonneUnter = $derived(zuMinuten(daten.basis?.sonne?.untergang));
  const jetztMin = $derived(jetztAmOrt.getHours() * 60 + jetztAmOrt.getMinutes());
  const jetztZeit = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", ...(zone ? { timeZone: zone } : {}) }));
  const istTag = $derived(jetztMin >= sonneAuf && jetztMin <= sonneUnter);
  const tagLaenge = $derived(sonneUnter - sonneAuf);
  const sonneWinkel = $derived.by(() => {
    if (!sonneAuf || !sonneUnter) return Math.PI / 2;
    if (istTag && tagLaenge > 0) return Math.PI * (1 - (jetztMin - sonneAuf) / tagLaenge);
    const nachtDauer = 1440 - sonneUnter + sonneAuf;
    const f = jetztMin >= sonneUnter ? (jetztMin - sonneUnter) / nachtDauer : (1440 - sonneUnter + jetztMin) / nachtDauer;
    return -Math.PI * f;
  });
  const sonneX = $derived(60 + 50 * Math.cos(sonneWinkel));
  const sonneY = $derived(60 - 50 * Math.sin(sonneWinkel));
  const sonneFarbe = $derived.by(() => {
    if (!istTag) return "var(--flaeche-3)";
    const f = (jetztMin - sonneAuf) / tagLaenge;
    if (f < 0.12) return "#FF9800";
    if (f < 0.3) return "#FFB74D";
    if (f < 0.7) return "#FFF59D";
    if (f < 0.88) return "#FFB74D";
    return "#FF7043";
  });
</script>

<div class="sm-bogen-wrap">
  <svg class="sm-bogen" viewBox="0 0 120 120" preserveAspectRatio="xMidYMid meet">
    <defs>
      <linearGradient id="sm-tag" x1="0%" y1="50%" x2="100%" y2="50%">
        <stop offset="0%" stop-color="#FF9800" /><stop offset="50%" stop-color="#FFEB3B" /><stop offset="100%" stop-color="#FF5722" />
      </linearGradient>
      <filter id="sm-glow" x="-120%" y="-120%" width="340%" height="340%">
        <feGaussianBlur stdDeviation="3.6" result="b" />
        <feMerge><feMergeNode in="b" /><feMergeNode in="b" /></feMerge>
      </filter>
    </defs>
    <path d="M 110 60 A 50 50 0 0 1 10 60" fill="none" stroke="var(--rand)" stroke-width="2" stroke-dasharray="3 4" />
    <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="url(#sm-tag)" stroke-width="2" stroke-linecap="round" />
    <line x1="5" y1="60" x2="115" y2="60" stroke="var(--rand-stark)" stroke-width="1" />
    {#if istTag}
      <circle class="sm-strahlen" cx={sonneX} cy={sonneY} r="15" fill={sonneFarbe} filter="url(#sm-glow)" />
    {/if}
    <circle cx={sonneX} cy={sonneY} r="11" fill={sonneFarbe} stroke={istTag ? "none" : "var(--rand-stark)"} stroke-width={istTag ? 0 : 2} stroke-dasharray={istTag ? "none" : "3 3"} />
  </svg>
  <div class="sm-mitte"><div class="sm-jetzt">Jetzt</div><div class="sm-zeit">{jetztZeit}</div></div>
</div>
<div class="sm-auf-unter">
  <span><span class="sm-lab">Aufgang</span><b><i class="fa-solid fa-arrow-up dimm"></i> {daten.basis?.sonne?.aufgang ?? "-"}</b></span>
  <span class="rechts"><span class="sm-lab">Untergang</span><b>{daten.basis?.sonne?.untergang ?? "-"} <i class="fa-solid fa-arrow-down dimm"></i></b></span>
</div>
