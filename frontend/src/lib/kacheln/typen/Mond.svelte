<script lang="ts">
  import { uhr } from "../../uhr.svelte";
  import { zeitzoneFuer } from "../../orte.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Datumsangaben in der Zeitzone des Ortes zeigen (die Mondphase selbst ist von der
  // Zeitzone unabhaengig, weil sie auf absoluter Zeit beruht).
  const zone = $derived(zeitzoneFuer(ort));
  const datumOpt = $derived(zone ? { timeZone: zone } : {});

  // Mondphase: rein rechnerisch (synodischer Monat).
  const SYNODISCH = 29.530588853;
  const NEUMOND0 = Date.UTC(2000, 0, 6, 18, 14, 0);
  const mond = $derived.by(() => {
    const tage = (uhr.jetzt.getTime() - NEUMOND0) / 86400000;
    const alter = ((tage % SYNODISCH) + SYNODISCH) % SYNODISCH;
    const phase = alter / SYNODISCH;
    const beleuchtung = Math.round(((1 - Math.cos(phase * 2 * Math.PI)) / 2) * 100);
    let emoji = "🌕";
    if (phase < 0.025 || phase >= 0.975) emoji = "🌑";
    else if (phase < 0.235) emoji = "🌒";
    else if (phase < 0.265) emoji = "🌓";
    else if (phase < 0.485) emoji = "🌔";
    else if (phase < 0.515) emoji = "🌕";
    else if (phase < 0.735) emoji = "🌖";
    else if (phase < 0.765) emoji = "🌗";
    else emoji = "🌘";
    const fmt = (d: number) =>
      new Date(uhr.jetzt.getTime() + d * 86400000).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", ...datumOpt });
    return {
      emoji,
      beleuchtung,
      zunehmend: phase < 0.5,
      naechsterNeu: fmt(((1 - phase) % 1) * SYNODISCH),
      naechsterVoll: fmt(((0.5 - phase + 1) % 1) * SYNODISCH),
    };
  });
  const heuteKurz = $derived.by(() => {
    const wd = uhr.jetzt.toLocaleDateString("de-DE", { weekday: "short", ...datumOpt }).replace(".", "");
    const dm = uhr.jetzt.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", ...datumOpt });
    return `${wd} ${dm}`;
  });
</script>

<div class="mond-datum">{heuteKurz}</div>
<div class="mond-haupt">
  <span class="mond-gross">{mond.emoji}</span>
  <span class="mond-werte">
    <span class="dimm klein-txt">{mond.zunehmend ? "Zunehmend" : "Abnehmend"}</span>
    <span class="mond-prozent tnum">{mond.beleuchtung}%</span>
    <span class="dimm klein-txt">beleuchtet</span>
  </span>
</div>
<div class="mond-daten">
  <span>🌑 Neumond {mond.naechsterNeu}</span>
  <span>🌕 Vollmond {mond.naechsterVoll}</span>
</div>
