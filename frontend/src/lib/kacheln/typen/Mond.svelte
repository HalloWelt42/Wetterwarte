<script lang="ts">
  import { uhr } from "../../../kern/uhr.svelte";
  import { zeitzoneFuer } from "../../../kern/orte.svelte";
  import { mondstand } from "../../../kern/mond";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Datumsangaben in der Zeitzone des Ortes zeigen (die Mondphase selbst ist von der
  // Zeitzone unabhaengig, weil sie auf absoluter Zeit beruht).
  const zone = $derived(zeitzoneFuer(ort));
  const datumOpt = $derived(zone ? { timeZone: zone } : {});

  // Mondphase aus dem gemeinsamen Kern (kern/mond.ts).
  const mond = $derived.by(() => {
    const m = mondstand(uhr.jetzt);
    const fmt = (d: number) =>
      new Date(uhr.jetzt.getTime() + d * 86400000).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", ...datumOpt });
    return {
      emoji: m.emoji,
      beleuchtung: Math.round(m.anteil * 100),
      zunehmend: m.zunehmend,
      naechsterNeu: fmt(m.tageBisNeu),
      naechsterVoll: fmt(m.tageBisVoll),
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
