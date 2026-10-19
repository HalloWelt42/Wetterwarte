<script lang="ts">
  // Blatt Luft: Luftqualitätsindex groß im Ring mit Stufe, alle Schadstoffe mit Balken zum
  // Richtwert für die Gesundheit, die Stufen des Index und die Fachbegriffe.
  import type { KachelProps } from "../kachelprops";
  import { luftVar, zahl } from "../format";
  import Ring from "../mikro/Ring.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { erklaerung } from "./erklaerungen";

  let { daten, zone }: KachelProps = $props();

  // Stufen des europäischen Index (wie die Quelle sie benennt)
  const STUFEN = [
    { bis: 20, text: "0 bis 20 · gut", rat: "" },
    { bis: 40, text: "21 bis 40 · ordentlich", rat: "" },
    { bis: 60, text: "41 bis 60 · mäßig", rat: "Empfindliche draußen ruhiger" },
    { bis: 80, text: "61 bis 80 · schlecht", rat: "Anstrengung draußen meiden" },
    { bis: 100, text: "81 bis 100 · sehr schlecht", rat: "Alle draußen ruhiger" },
    { bis: Infinity, text: "über 100 · extrem schlecht", rat: "Möglichst drinnen bleiben" },
  ];
  // Richtwerte für die Gesundheit als Tagesmittel in µg/m³, mit Formel und Herkunft
  const STOFFE: Record<string, { richtwert: number; formel: [string, string]; herkunft: string }> = {
    no2: { richtwert: 25, formel: ["NO", "2"], herkunft: "vor allem aus dem Verkehr" },
    o3: { richtwert: 100, formel: ["O", "3"], herkunft: "entsteht bei Sonne aus Abgasen" },
    pm2_5: { richtwert: 15, formel: ["PM", "2,5"], herkunft: "sehr feine Teilchen" },
    pm10: { richtwert: 45, formel: ["PM", "10"], herkunft: "gröbere Teilchen" },
  };

  const luft = $derived(daten.luft);
  const bereich = $derived(daten.bereiche.luft);
  const stufe = $derived(luft ? STUFEN.findIndex((s) => luft.index <= s.bis) : -1);
  const STUFEN_FARBE = ["--gut", "--gut", "--w1", "--w2", "--w3", "--w4"];
  function balkenFarbe(anteil: number): string {
    if (anteil <= 0.5) return "--gut";
    if (anteil <= 1) return "--w1";
    if (anteil <= 2) return "--w2";
    return "--w3";
  }
</script>

{#if !luft}
  <div class="abschnitt">
    {#if bereich.status === "fehlt"}
      <Hinweis titel="Luftdaten fehlen" text="Die Quelle für die Luftqualität antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    {:else}
      <Hinweis symbol="fa-lungs" titel="Keine Luftdaten für diesen Ort" text="Die Quelle liefert für diesen Ort keine Werte zur Luftqualität." />
    {/if}
    <Stand {bereich} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <div class="held-bild ring">
        <Ring wert={luft.index} max={100} farbe={luftVar(luft.index)} />
        <div class="mitte"><div class="riesen-zahl mittel">{zahl(luft.index)}</div></div>
      </div>
      <div class="held-text">
        <div class="held-satz">{luft.stufe || "Stufe unbekannt"}</div>
        <div class="held-unter">Europäischer Luftqualitätsindex, kleiner ist besser.</div>
      </div>
    </div>
  </div>

  {#if luft.schadstoffe.length}
    <div class="abschnitt">
      <h3>Schadstoffe</h3>
      <div class="zeilen">
        {#each luft.schadstoffe as s (s.schluessel)}
          {@const stoff = STOFFE[s.schluessel]}
          {@const anteil = stoff ? s.wert / stoff.richtwert : 0}
          <div class="zeile schad">
            <div class="schad-kopf">
              <b>{s.titel}</b>
              <span>{zahl(s.wert)} <small>{stoff ? `von ${stoff.richtwert} ${s.einheit}` : s.einheit}</small></span>
            </div>
            {#if stoff}
              <div class="bz-bahn"><span style="width: {Math.min(100, anteil * 100)}%; background: var({balkenFarbe(anteil)})"></span></div>
              <div class="schad-unter">{stoff.formel[0]}<sub>{stoff.formel[1]}</sub>, {stoff.herkunft}{#if anteil > 1}, <b>über dem Richtwert</b>{/if}</div>
            {/if}
          </div>
        {/each}
      </div>
      <p>Werte in Mikrogramm je Kubikmeter Luft. Der Balken zeigt den Anteil am Richtwert für die Gesundheit (Tagesmittel).</p>
    </div>
  {/if}

  <div class="abschnitt">
    <h3>Stufen</h3>
    <div class="zeilen">
      {#each STUFEN as s, i (s.text)}
        <div class="zeile" class:an={i === stufe}>
          <span class="farbpunkt" style="background: var({STUFEN_FARBE[i]})"></span>
          <div class="haupt"><b>{s.text}</b>{#if s.rat}<small>{s.rat}</small>{/if}</div>
        </div>
      {/each}
    </div>
    <Stand {bereich} {zone} />
  </div>

  <Begriffe liste={[erklaerung.luftindex, erklaerung.feinstaub, erklaerung.ozon, erklaerung.stickstoffdioxid]} />
{/if}

<style>
  .ring {
    width: 120px;
    height: 120px;
  }
</style>
