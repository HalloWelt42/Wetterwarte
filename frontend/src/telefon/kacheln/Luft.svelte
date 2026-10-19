<script lang="ts">
  // Luft: europäischer Luftqualitätsindex als Ring mit Stufe. 1x1 Ring und Wort, 2x1 dazu die zwei
  // auffälligsten Schadstoffe, 3x1 alle vier, 2x2 Ring mit Stufe und vier Balken, 3x2 mit vollen
  // Namen. Die Balken zeigen den Anteil am Richtwert (PM2,5 25, PM10 50, Ozon 180, NO2 200 µg/m³).
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { luftVar, zahl } from "../format";
  import KKopf from "../KKopf.svelte";
  import Ring from "../mikro/Ring.svelte";

  let { kachel, daten }: KachelProps = $props();

  // Kurzzeichen mit tiefgestellter Ziffer und Richtwert (100 %) je Schadstoff
  const STOFFE: Record<string, { zeichen: string; tief: string; grenze: number; kurz: string }> = {
    pm2_5: { zeichen: "PM", tief: "2,5", grenze: 25, kurz: "Feinstaub" },
    pm10: { zeichen: "PM", tief: "10", grenze: 50, kurz: "Feinstaub" },
    o3: { zeichen: "O", tief: "3", grenze: 180, kurz: "Ozon" },
    no2: { zeichen: "NO", tief: "2", grenze: 200, kurz: "Stickstoff\u00ADdioxid" }, // weiches Trennzeichen
  };

  const f = $derived(form(kachel));
  const luft = $derived(daten.luft);
  const farbe = $derived(luft ? luftVar(luft.index) : "--gut");
  // Nach Anteil am Richtwert, der auffälligste zuerst; ohne Richtwert ans Ende
  const stoffe = $derived(
    (luft?.schadstoffe ?? [])
      .map((s) => {
        const st = STOFFE[s.schluessel];
        return { ...s, st, anteil: st ? s.wert / st.grenze : -1 };
      })
      .sort((a, b) => b.anteil - a.anteil),
  );
  const auffaellig = $derived(stoffe[0]?.st?.kurz ?? null);
  const anzahl = $derived(f === "2x1" ? 2 : 4);
</script>

{#snippet balken(voll: boolean)}
  {#each stoffe.slice(0, anzahl) as s, i (s.schluessel)}
    <div class="balken-z" class:voll class:entbehrlich-gross={f === "3x1" && i === 3} class:entbehrlich={f === "3x1" && i === 2}>
      <span class="bz-lab">{#if voll}{s.titel}{:else if s.st}{s.st.zeichen}<sub>{s.st.tief}</sub>{:else}{s.titel}{/if}</span>
      <span class="bz-bahn"><span style="width: {Math.min(100, Math.max(0, s.anteil) * 100)}%; background: var({farbe})"></span></span>
      <span class="bz-wert">{zahl(s.wert)}</span>
    </div>
  {/each}
{/snippet}

{#snippet ring()}
  <Ring wert={luft?.index ?? 0} max={100} {farbe} />
  <b>{luft?.index}</b>
{/snippet}

{#if !luft}
  <KKopf titel="Luft" symbol="fa-lungs" />
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if f === "1x1"}
  <KKopf titel="Luft" symbol="fa-lungs" />
  <div class="ringwert ring-klein">{@render ring()}</div>
  <div class="unter mittig">{luft.stufe}</div>
{:else if f === "2x1" || f === "3x1"}
  <KKopf titel="Luft" symbol="fa-lungs" rechts={luft.stufe} />
  <div class="k-reihe mitte">
    <div class="ringwert ring-hoch">{@render ring()}</div>
    <div class="k-block dehnen liste" class:eng={f === "3x1"}>{@render balken(false)}</div>
  </div>
{:else}
  <KKopf titel="Luft" symbol="fa-lungs" rechts="µg/m³" />
  <div class="k-reihe mitte" style="margin-top: 4px">
    <div class="ringwert ring-hoch">{@render ring()}</div>
    <div class="k-block dehnen">
      <div class="zustand">{luft.stufe}</div>
      {#if auffaellig}<div class="unter umbruch">vor allem {auffaellig}</div>{/if}
    </div>
  </div>
  <div class="liste unten">{@render balken(f === "3x2")}</div>
{/if}

<style>
  .ring-klein {
    flex: 1 1 0;
    min-height: 0;
    margin: 4px auto 0;
  }
  /* Zusatz unter der Stufe darf auf zwei Zeilen umbrechen */
  .unter.umbruch {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .ring-hoch {
    height: 100%;
  }
  .mittig {
    text-align: center;
  }
  .liste {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  /* Vier Balken in einer Reihe von 1 Feld Höhe: enger gesetzt */
  .liste.eng {
    gap: 3px;
  }
  .liste.eng .balken-z {
    line-height: 1.1;
  }
  .liste.unten {
    flex: none;
    gap: 7px;
    margin-top: 10px;
  }
  /* Volle Namen (3x2): breitere Spalte für die Bezeichnung */
  .balken-z.voll {
    grid-template-columns: 8.6em minmax(0, 1fr) 2.2em;
  }
  .balken-z.voll .bz-lab {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
