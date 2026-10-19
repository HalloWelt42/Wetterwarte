<script lang="ts">
  // Blatt UV: UV-Index jetzt im großen Bogen mit Rat, Tageskurve heute und morgen aus den
  // Stundenwerten bei Tag, die Stufen mit ihrem Schutz und der Fachbegriff.
  import type { KachelProps } from "../kachelprops";
  import { stunde } from "../../kern/zeit";
  import { uvWort, zahl } from "../format";
  import Bogen from "../mikro/Bogen.svelte";
  import Linie from "../mikro/Linie.svelte";
  import Achse from "./bausteine/Achse.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Segmente from "./bausteine/Segmente.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { gross, kalendertag } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { uvRat, uvZahl } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const STUFEN = [
    { ab: 0, bis: 3, text: "0 bis 2 · gering", rat: "kein Schutz nötig", farbe: "--gut" },
    { ab: 3, bis: 6, text: "3 bis 5 · mäßig", rat: "mittags Schatten, Sonnencreme", farbe: "--w1" },
    { ab: 6, bis: 8, text: "6 bis 7 · hoch", rat: "Hut, Sonnenbrille, Sonnencreme", farbe: "--w2" },
    { ab: 8, bis: 11, text: "8 bis 10 · sehr hoch", rat: "mittags drinnen bleiben", farbe: "--w3" },
    { ab: 11, bis: Infinity, text: "ab 11 · extrem", rat: "Sonne meiden", farbe: "--w4" },
  ];

  const uv = $derived(daten.jetzt?.uv ?? null);
  let welcher = $state<"0" | "1">("0");
  const tag = $derived(daten.tage[Number(welcher)] ?? null);
  // Tageskurve: Stunden dieses Kalendertags bei Tag (Stundenwerte reichen 6 Stunden zurück)
  const kurve = $derived(tag ? daten.stunden.filter((s) => s.tag && kalendertag(s.zeit, zone) === tag.datum) : []);
  const spitze = $derived(kurve.length ? kurve.reduce((m, s) => (s.uv > m.uv ? s : m), kurve[0]) : null);
  const jetztIndex = $derived(kurve.findIndex((s) => s.zeit === daten.stunden[daten.jetzt_index]?.zeit));
  const marken = $derived(
    kurve
      .map((s, i) => ({ s, i }))
      .filter(({ i }) => i % 2 === 0)
      .map(({ s, i }) => ({ anteil: i / Math.max(1, kurve.length - 1), text: String(stunde(s.zeit, zone)).padStart(2, "0") })),
  );
  const heuteMax = $derived(daten.tage[0]?.uv_max ?? null);
  const heuteSpitze = $derived.by(() => {
    const t = daten.tage[0];
    if (!t) return null;
    const h = daten.stunden.filter((s) => s.tag && kalendertag(s.zeit, zone) === t.datum);
    return h.length ? h.reduce((m, s) => (s.uv > m.uv ? s : m), h[0]) : null;
  });
  // Die Stundenwerte reichen nur 6 Stunden zurück: fehlt heute der Morgen, steht ein Hinweis da
  const frueherFehlt = $derived(
    !!tag?.sonnenaufgang && kurve.length > 0 && new Date(kurve[0].zeit).getTime() - new Date(tag.sonnenaufgang).getTime() > 3_600_000,
  );
  const stufe = (v: number) => STUFEN.findIndex((s) => v >= s.ab && v < s.bis);
</script>

{#if uv === null}
  <div class="abschnitt">
    <Hinweis titel="UV-Index fehlt" text="Die Wetterquelle antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <div class="held-bild bogen">
        <Bogen wert={uv} max={11} />
        <div class="mitte"><div class="riesen-zahl">{uvZahl(uv)}</div></div>
      </div>
      <div class="held-text">
        <div class="held-satz">{gross(uvWort(uv))}</div>
        <div class="held-unter">
          {#if heuteMax !== null}
            Heute höchstens <b>{uvZahl(heuteMax)}</b>{#if heuteSpitze && heuteSpitze.uv > 0}{" "}gegen {stunde(heuteSpitze.zeit, zone)} Uhr{/if}.
            {uvRat(heuteMax)}
          {:else}
            {uvRat(uv)}
          {/if}
        </div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Tageskurve</h3>
    <Segmente optionen={[{ wert: "0", titel: "Heute" }, { wert: "1", titel: "Morgen" }]} bind:wert={welcher} />
    <div class="tafel">
      {#if tag}
        <div class="tafel-kopf">
          <b>Höchstwert {uvZahl(tag.uv_max)}</b>
          <span>{#if spitze && spitze.uv > 0}gegen {stunde(spitze.zeit, zone)} Uhr,{" "}{/if}{uvWort(tag.uv_max)}</span>
        </div>
        {#if kurve.length > 1}
          <div class="diagramm mittel"><Linie werte={kurve.map((s) => s.uv)} farbe="--sonne" flaeche jetzt={jetztIndex} einheit="" /></div>
          <Achse {marken} />
          {#if frueherFehlt}<div class="tafel-fuss">Frühere Stunden von heute liegen nicht mehr vor.</div>{/if}
        {:else}
          <Hinweis symbol="fa-moon" titel="Keine Stundenwerte bei Tag" text="Für heute liegen keine Stunden mit Tageslicht mehr vor. Der Höchstwert oben gilt für den ganzen Tag." />
        {/if}
      {:else}
        <Hinweis titel="Keine Vorhersage für diesen Tag" />
      {/if}
    </div>
  </div>

  <div class="abschnitt">
    <h3>Stufen</h3>
    <div class="zeilen">
      {#each STUFEN as s, i (s.text)}
        <div class="zeile" class:an={i === stufe(uv)}>
          <span class="farbpunkt" style="background: var({s.farbe})"></span>
          <div class="haupt"><b>{s.text}</b><small>{s.rat}</small></div>
        </div>
      {/each}
    </div>
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>

  <Begriffe liste={[erklaerung.uv]} />
{/if}

<style>
  .bogen {
    width: 150px;
    height: 130px;
  }
</style>
