<script lang="ts">
  // UV-Index: 1x1 Bogen mit Wert in der Mitte und Wort, 2x1 Wert und Tageskurve, 3x1 Kurve breit mit
  // Stundenachse, 2x2 großer Bogen und Kurve. Die Tageskurve kommt aus den Stunden von heute, soweit
  // die Liste sie enthält (sie beginnt 6 Stunden vor jetzt); Höchstwert und seine Uhrzeit aus der
  // Tagesvorhersage (das Backend kennt den ganzen Tag).
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { stunde } from "../../kern/zeit";
  import { uvWort, zahl } from "../format";
  import KKopf from "../KKopf.svelte";
  import Bogen from "../mikro/Bogen.svelte";
  import Linie from "../mikro/Linie.svelte";
  import { stundenHeute } from "./tageslauf";

  let { kachel, daten, zone }: KachelProps = $props();

  const f = $derived(form(kachel));
  const uv = $derived(daten.jetzt ? Math.round(daten.jetzt.uv) : null);
  const heute = $derived(stundenHeute(daten, zone));

  // Tageskurve: von der Stunde vor dem ersten bis zur Stunde nach dem letzten Wert über 0
  const kurve = $derived.by(() => {
    const hell = heute.filter(({ s }) => s.uv > 0);
    if (!hell.length) return null;
    const von = Math.max(0, heute.indexOf(hell[0]) - 1);
    const bis = Math.min(heute.length - 1, heute.indexOf(hell[hell.length - 1]) + 1);
    const teil = heute.slice(von, bis + 1);
    return { stunden: teil, werte: teil.map(({ s }) => s.uv), jetzt: teil.findIndex(({ i }) => i === daten.jetzt_index) };
  });

  const spitze = $derived.by(() => {
    const tag = daten.tage[0];
    if (!tag) return "";
    return `Spitze ${zahl(Math.round(tag.uv_max))}${tag.uv_max_zeit ? ` um ${stunde(tag.uv_max_zeit, zone)} Uhr` : ""}`;
  });

  // Stundenachse unter der breiten Kurve: höchstens fünf Marken
  const marken = $derived.by(() => {
    if (!kurve) return [];
    const n = kurve.stunden.length;
    const schritt = Math.max(1, Math.ceil((n - 1) / 4));
    const ks: number[] = [];
    for (let k = 0; k < n; k += schritt) ks.push(k);
    // Die letzte Stunde steht immer da; liegt die Marke davor zu nah, weicht sie
    if (ks[ks.length - 1] !== n - 1) {
      if (n - 1 - ks[ks.length - 1] < schritt / 2) ks.pop();
      ks.push(n - 1);
    }
    return ks.map((k) => ({
      k,
      text: String(stunde(kurve.stunden[k].s.zeit, zone)).padStart(2, "0"),
      lage: n > 1 ? k / (n - 1) : 0,
    }));
  });
</script>

{#snippet tageskurve()}
  <div class="kurve">
    {#if kurve}
      <Linie werte={kurve.werte} farbe="--sonne" flaeche jetzt={kurve.jetzt} />
    {:else}
      <div class="im-feld">kein Verlauf</div>
    {/if}
  </div>
{/snippet}

{#if uv === null}
  <KKopf titel="UV" symbol="fa-sun" />
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if f === "1x1"}
  <KKopf titel="UV" symbol="fa-sun" />
  <div class="ringwert bogen-klein">
    <Bogen wert={uv} max={11} />
    <b>{uv}</b>
  </div>
  <div class="unter mittig">{uvWort(uv)}</div>
{:else if f === "2x1"}
  <KKopf titel="UV" symbol="fa-sun" rechts={spitze} />
  <div class="k-reihe">
    <div class="k-block">
      <div class="wert dick"><b>{uv}</b></div>
      <div class="unter">{uvWort(uv)}</div>
    </div>
    {@render tageskurve()}
  </div>
{:else if f === "3x1"}
  <KKopf titel="UV" symbol="fa-sun" rechts={spitze} />
  <div class="k-reihe">
    <div class="k-block">
      <div class="wert dick"><b>{uv}</b></div>
      <div class="unter">{uvWort(uv)}</div>
    </div>
    <div class="breit">
      {@render tageskurve()}
      <div class="achse">
        {#each marken as m (m.k)}
          <span style="left: calc(5px + (100% - 10px) * {m.lage})" class:anfang={m.lage === 0} class:ende={m.lage === 1}>{m.text}</span>
        {/each}
      </div>
    </div>
  </div>
{:else}
  <KKopf titel="UV" symbol="fa-sun" rechts={spitze} />
  <div class="ringwert bogen-gross">
    <Bogen wert={uv} max={11} />
    <b>{uv}</b>
  </div>
  <div class="zustand mittig">{uvWort(uv)}</div>
  <div class="kurve-fest">{@render tageskurve()}</div>
{/if}

<style>
  /* Bogen füllt die Höhe; die Öffnung unten nimmt das Wort darunter auf */
  .bogen-klein {
    flex: 1 1 0;
    min-height: 0;
    margin: 2px auto -6px;
  }
  .bogen-gross {
    flex: 1 1 0;
    min-height: 0;
    margin: 4px auto -10px;
  }
  .mittig {
    text-align: center;
  }
  .kurve {
    flex: 1 1 0;
    min-width: 0;
    min-height: 0;
    align-self: stretch;
    display: flex;
    position: relative;
  }
  .kurve-fest {
    flex: none;
    height: 44px;
    display: flex;
    margin-top: 4px;
  }
  /* Breite Kurve mit Stundenachse darunter */
  .breit {
    flex: 1 1 0;
    min-width: 0;
    align-self: stretch;
    display: flex;
    flex-direction: column;
  }
  .achse {
    position: relative;
    flex: none;
    height: calc(var(--s13) * 1.15);
    margin-top: 2px;
  }
  .achse span {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    font-size: var(--s13);
    font-weight: 700;
    color: var(--text-3);
    line-height: 1.15;
    white-space: nowrap;
  }
  .achse span.anfang {
    transform: translateX(-5px);
  }
  .achse span.ende {
    transform: translateX(calc(-100% + 5px));
  }
</style>
