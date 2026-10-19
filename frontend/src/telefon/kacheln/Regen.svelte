<script lang="ts">
  import { kalendertag, stunde } from "../../kern/zeit";
  // Regen: Kurzfrist für rund 2 Stunden (mm/h, Radar vor Modell). 1x1 ein Satz ("beginnt in" 25 "Minuten",
  // "regnet noch", "trocken bis 17 Uhr"; die Einheit steht ausgeschrieben in eigener Zeile), 2x1 Satz und
  // Säulen, 3x1 zusätzlich Achse jetzt, +1 h, +2 h. Bleibt es 2 Stunden trocken, sagt die Stundenvorhersage,
  // bis wann.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { zahl } from "../format";
  import { regenAb, regenAbText } from "../rechnen";
  import type { Stunde } from "../typen";
  import KKopf from "../KKopf.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  

  let { kachel, daten, zone }: KachelProps = $props();

  type Lage =
    | { art: "regnet"; ende: number | null }
    | { art: "beginnt"; min: number }
    | { art: "trocken-bis"; s: Stunde; morgen: boolean }
    | { art: "trocken-2h" } // die Stunden melden Regen schon in den 2 Stunden, die Kurzfrist nicht
    | { art: "trocken-24h" };

  const f = $derived(form(kachel));
  const r = $derived(daten.regen);
  const bezug = $derived(daten.jetzt?.zeit ?? daten.zeit);
  const lage = $derived.by((): Lage | null => {
    if (!r) return null;
    if (r.beginn_min === 0) return { art: "regnet", ende: r.ende_min };
    if (r.beginn_min !== null) return { art: "beginnt", min: r.beginn_min };
    const s = regenAb(daten);
    if (!s) return { art: "trocken-24h" };
    if (Date.parse(s.zeit) < Date.parse(bezug) + (r.werte.length * r.schritt_min - 1) * 60_000) return { art: "trocken-2h" };
    return { art: "trocken-bis", s, morgen: kalendertag(s.zeit, zone) !== kalendertag(bezug, zone) };
  });
  // 1x1: Einheit in eigener Zeile statt abgekürzt neben der Zahl
  const klein = $derived(f === "1x1");
  const spitze = $derived(r ? zahl(r.max_mm_h, r.max_mm_h < 10 ? 1 : 0) : "");

  /** Stärke in Worten (leicht unter 2,5 mm/h, mäßig bis 10, darüber kräftig). */
  function staerke(mmh: number): string {
    if (mmh < 2.5) return "leicht";
    if (mmh < 10) return "mäßig";
    return "kräftig";
  }
</script>

{#snippet satz(klasse: string)}
  {#if lage?.art === "regnet" && lage.ende !== null}
    <div class="vor">regnet noch</div>
    {#if klein}
      <div class="wert {klasse} c-regen"><b>{lage.ende}</b></div>
      <div class="unter">Minuten</div>
    {:else}
      <div class="wert {klasse} c-regen"><b>{lage.ende}</b><small>Minuten</small></div>
      <div class="unter entbehrlich">bis <b>{spitze}</b> mm/h</div>
    {/if}
  {:else if lage?.art === "regnet"}
    <div class="vor">regnet</div>
    <div class="wert {klasse} c-regen"><b>{spitze}</b><small>mm/h</small></div>
    <div class="unter entbehrlich">noch über 2 Stunden</div>
  {:else if lage?.art === "beginnt"}
    <div class="vor">beginnt in</div>
    {#if klein}
      <div class="wert {klasse} c-regen"><b>{lage.min}</b></div>
      <div class="unter">Minuten</div>
    {:else}
      <div class="wert {klasse} c-regen"><b>{lage.min}</b><small>Minuten</small></div>
      <div class="unter entbehrlich">
        {#if f === "2x1"}{staerke(r?.max_mm_h ?? 0)}{:else}bis <b>{spitze}</b> mm/h{/if}
      </div>
    {/if}
  {:else if lage?.art === "trocken-bis"}
    {@const menge = lage.s.regen_wahrsch !== null ? `${zahl(lage.s.regen_wahrsch)} %` : `${zahl(lage.s.regen_mm, 1)} mm`}
    {#if lage.morgen && f === "1x1"}
      <!-- 1x1 hat für "trocken bis morgen" keinen Platz: "morgen ab 7 Uhr" sagt dasselbe -->
      <div class="vor">morgen ab</div>
      <div class="wert {klasse} c-regen"><b>{stunde(lage.s.zeit, zone)}</b><small>Uhr</small></div>
      <div class="unter entbehrlich"><b>{menge}</b> Regen</div>
    {:else}
      <div class="vor">trocken bis{lage.morgen ? " morgen" : ""}</div>
      <div class="wert {klasse} c-regen"><b>{stunde(lage.s.zeit, zone)}</b><small>Uhr</small></div>
      <div class="unter entbehrlich">dann <b>{menge}</b></div>
    {/if}
  {:else if lage}
    <div class="vor">kein Regen in</div>
    {#if klein}
      <div class="wert {klasse} c-regen"><b>{lage.art === "trocken-2h" ? 2 : 24}</b></div>
      <div class="unter">Stunden</div>
    {:else}
      <div class="wert {klasse} c-regen"><b>{lage.art === "trocken-2h" ? 2 : 24}</b><small>Stunden</small></div>
      {#if lage.art === "trocken-2h"}<div class="unter entbehrlich">dann möglich</div>{/if}
    {/if}
  {/if}
{/snippet}

{#if !r}
  <KKopf titel="Regen" symbol="fa-umbrella" rechts={f === "1x1" ? "" : regenAbText(daten)} />
  <div class="k-mitte">
    <div class="k-hinweis drei">keine Kurzfrist&shy;vorhersage</div>
  </div>
{:else if f === "1x1"}
  <KKopf titel="Regen" symbol="fa-umbrella" />
  <div class="k-fuss">{@render satz("")}</div>
{:else}
  <KKopf titel="Regen" symbol="fa-umbrella" rechts={f === "2x1" ? "2 Stunden" : "nächste 2 Stunden"} />
  <div class="k-reihe">
    <div class="k-block" class:breit={f === "3x1"}>{@render satz("halb")}</div>
    <div class="saeulen">
      <Saeulen werte={r.werte} max={2} achse={f === "3x1" ? ["jetzt", "+1 h", "+2 h"] : []} />
      {#if r.beginn_min === null}
        <div class="im-feld" class:mit-achse={f === "3x1"} class:entbehrlich={f === "2x1"}>{f === "3x1" ? "kein Regen in 2 Stunden" : "kein Regen"}</div>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* In 1x1 braucht der Hinweis drei Zeilen */
  .k-hinweis.drei {
    -webkit-line-clamp: 3;
    line-clamp: 3;
  }
  /* 3x1: Wert so hoch wie in 2x1, damit Satzanfang, Wert und Zusatz in die Reihe passen */
  .breit .wert b {
    font-size: clamp(26px, 10.6cqi, 46px);
  }
  /* Säulen füllen die Resthöhe neben dem Satz; der Hinweis liegt darüber */
  .saeulen {
    flex: 1 1 0;
    min-width: 0;
    align-self: stretch;
    display: flex;
    position: relative;
  }
</style>
