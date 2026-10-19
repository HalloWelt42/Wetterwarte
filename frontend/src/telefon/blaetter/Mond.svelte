<script lang="ts">
  // Blatt Mond: Scheibe groß mit beleuchtetem Anteil und Phase, die nächsten Hauptphasen mit Datum
  // in Ortszeit. Rein gerechnet (kern/mond.ts), braucht keine Quelle.
  import type { KachelProps } from "../kachelprops";
  import { mondstand, SYNODISCH } from "../../kern/mond";
  import { uhr } from "../../kern/uhr.svelte";
  import { zahl } from "../format";
  import Mondscheibe from "../mikro/Mondscheibe.svelte";
  import Symbol from "../Symbol.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import { gross, kalendertag, tagLang, tageZwischen } from "./datum";
  import { erklaerung } from "./erklaerungen";

  let { zone }: KachelProps = $props();

  const PHASEN = [
    { phase: 0.5, titel: "Vollmond", bild: "moon-full" },
    { phase: 0.75, titel: "Letztes Viertel", bild: "moon-last-quarter" },
    { phase: 0, titel: "Neumond", bild: "moon-new" },
    { phase: 0.25, titel: "Erstes Viertel", bild: "moon-first-quarter" },
  ];

  // Minütlich rechnen genügt
  const minute = $derived(Math.floor(uhr.jetzt.getTime() / 60_000) * 60_000);
  const m = $derived(mondstand(new Date(minute)));
  const heute = $derived(kalendertag(new Date(minute), zone));
  const naechste = $derived(
    PHASEN.map((p) => {
      const tage = (((p.phase - m.phase + 1) % 1) || 1) * SYNODISCH;
      const datum = kalendertag(new Date(minute + tage * 86_400_000), zone);
      return { ...p, datum, inTagen: tageZwischen(heute, datum) };
    }).sort((a, b) => a.inTagen - b.inTagen),
  );
  const vollIn = $derived(naechste.find((p) => p.phase === 0.5)!);
  const wann = (n: number) => (n === 0 ? "heute" : n === 1 ? "morgen" : `in ${n} Tagen`);
</script>

<div class="abschnitt">
  <div class="held">
    <div class="held-bild scheibe"><Mondscheibe anteil={m.anteil} zunehmend={m.zunehmend} /></div>
    <div class="held-text">
      <div class="riesen-zahl">{zahl(m.anteil * 100)}<small>%</small></div>
      <div class="held-satz">{gross(m.name)}</div>
      <div class="held-unter">
        {#if m.name === "Vollmond"}Heute ist Vollmond{:else}Vollmond <b>{wann(vollIn.inTagen)}</b>, {tagLang(vollIn.datum)}{/if}
      </div>
    </div>
  </div>
</div>

<div class="abschnitt">
  <h3>Nächste Phasen</h3>
  <div class="zeilen">
    {#each naechste as p (p.titel)}
      <div class="zeile">
        <Symbol name={p.bild} />
        <div class="haupt"><b>{p.titel}</b><small>{wann(p.inTagen)}</small></div>
        <span class="rechts">{tagLang(p.datum)}</span>
      </div>
    {/each}
  </div>
  <p>Gerechnet aus dem mittleren Mondumlauf, auf etwa einen Tag genau. Der Tag gilt in der Zeitzone des Orts.</p>
</div>

<Begriffe liste={[erklaerung.mondAnteil]} />

<style>
  .scheibe {
    width: 116px;
    height: 116px;
  }
</style>
