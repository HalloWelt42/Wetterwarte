<script lang="ts">
  // Mond: 1x1 Scheibe, Anteil und Phase kurz; 2x1 Scheibe, Anteil, Phase in Worten und die Tage bis
  // zum nächsten Vollmond. Gerechnet im Gerät (kern/mond.ts), Kalendertage in Ortszeit.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { mondstand, SYNODISCH } from "../../kern/mond";
  import { uhr } from "../../kern/uhr.svelte";
  import { tageBis } from "../../kern/zeit";
  import KKopf from "../KKopf.svelte";
  import Mondscheibe from "../mikro/Mondscheibe.svelte";

  let { kachel, zone }: KachelProps = $props();

  const TAG_MS = 86_400_000;

  const f = $derived(form(kachel));
  const m = $derived(mondstand(uhr.jetzt));
  const prozent = $derived(Math.round(m.anteil * 100));
  // Kurzform: Neu- und Vollmond beim Namen, sonst nur, ob er zu- oder abnimmt
  const kurz = $derived(m.name === "Neumond" || m.name === "Vollmond" ? m.name : m.zunehmend ? "zunehmend" : "abnehmend");
  // Erster Buchstabe groß, weil die Phase allein in der Zeile steht ("Zunehmende Sichel")
  const phase = $derived(m.name.charAt(0).toUpperCase() + m.name.slice(1));
  const vollmond = $derived.by(() => {
    const naechster = uhr.jetzt.getTime() + m.tageBisVoll * TAG_MS;
    if (tageBis(new Date(naechster - SYNODISCH * TAG_MS), uhr.jetzt, zone) === 0) return { tage: 0, text: "Vollmond heute" };
    const tage = tageBis(new Date(naechster), uhr.jetzt, zone);
    return { tage, text: tage === 0 ? "Vollmond heute" : tage === 1 ? "Vollmond morgen" : `Vollmond in ${tage} Tagen` };
  });
</script>

{#if f === "1x1"}
  <KKopf titel="Mond" />
  <div class="scheibe-ecke"><Mondscheibe anteil={m.anteil} zunehmend={m.zunehmend} /></div>
  <div class="k-fuss">
    <div class="wert"><b>{prozent}</b><small>%</small></div>
    <div class="unter">{kurz}</div>
    {#if vollmond.tage > 1}<div class="unter entbehrlich-gross">voll in <b>{vollmond.tage}</b> Tagen</div>{/if}
  </div>
{:else}
  <KKopf titel="Mond" symbol="fa-moon" rechts={vollmond.text} />
  <div class="k-reihe mitte">
    <div class="scheibe"><Mondscheibe anteil={m.anteil} zunehmend={m.zunehmend} /></div>
    <div class="k-block dehnen">
      <div class="wert halb"><b>{prozent}</b><small>%</small></div>
      <div class="unter"><span class="lang">{phase}</span><span class="kurz">{kurz}</span></div>
    </div>
  </div>
{/if}

<style>
  /* 1x1: Scheibe oben rechts neben dem Kopf */
  .scheibe-ecke {
    position: absolute;
    right: 10px;
    top: 10px;
    width: 40px;
    height: 40px;
    display: flex;
  }
  /* Ab großer Schrift die Kurzform der Phase, damit nichts abgeschnitten wird */
  .kurz {
    display: none;
  }
  :global(.tel[data-stufe="gross"]) .lang,
  :global(.tel[data-stufe="sehr-gross"]) .lang {
    display: none;
  }
  :global(.tel[data-stufe="gross"]) .kurz,
  :global(.tel[data-stufe="sehr-gross"]) .kurz {
    display: inline;
  }
  /* 2x1: Scheibe so hoch wie die Reihe */
  .scheibe {
    align-self: stretch;
    aspect-ratio: 1;
    flex: none;
    display: flex;
  }
</style>
