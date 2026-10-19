<script lang="ts">
  // Messwert: ein Wert jetzt mit Verlauf aus den Stunden (Einstellung "groesse"). 1x1 Wert mit
  // kurzem Verlauf (6 Stunden zurück, 6 voraus), 2x1 Verlauf 24 h (6 zurück, 18 voraus), 3x1 Verlauf
  // 48 h mit Tief und Hoch. Der Punkt steht auf jetzt; Regen heute zeigt Säulen in mm je Stunde.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { einstellung } from "../../kern/gemeinsam";
  import KKopf from "../KKopf.svelte";
  import Linie from "../mikro/Linie.svelte";
  import Ring from "../mikro/Ring.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  import { druckTendenz, messwertVon, verlauf } from "./messwerte";

  let { kachel, daten }: KachelProps = $props();

  const f = $derived(form(kachel));
  const m = $derived(messwertVon(einstellung("messwert", kachel.conf, "groesse")));
  const wert = $derived(m.jetzt(daten));
  const voraus = $derived(f === "1x1" ? 6 : f === "2x1" ? 18 : 42);
  const reihe = $derived(verlauf(daten, m, 6, voraus));
  const tendenz = $derived(m.art === "druck" ? druckTendenz(daten.jetzt?.druck_tendenz ?? null) : null);
  const zusatz = $derived(wert === null ? null : m.zusatz(daten, wert, f !== "3x1"));
  const trocken = $derived(m.saeulen && !!reihe && reihe.werte.every((v) => v <= 0));
</script>

{#snippet dicke(klasse: string)}
  {#if wert === null}
    <div class="k-hinweis">keine Angabe</div>
  {:else}
    <div class="wert {klasse} {m.klasse(wert)}">
      <b>{m.text(wert)}</b>{#if m.einheit}<small>{m.einheit}</small>{/if}{#if tendenz}<i class="fa-solid {tendenz.pfeil} pfeil"></i>{/if}
    </div>
  {/if}
{/snippet}

{#snippet zeile(klasse: string)}
  {#if zusatz?.text}<div class="unter {klasse}">{zusatz.text}{#if zusatz.fett}{" "}<b>{zusatz.fett}</b>{/if}</div>{/if}
{/snippet}

{#snippet verlaufFeld()}
  <div class="verlauf">
    {#if !reihe}
      <div class="im-feld">kein Verlauf</div>
    {:else if m.saeulen}
      <Saeulen werte={reihe.werte} max={1} farbe={m.farbe} />
      {#if trocken}<div class="im-feld">trocken</div>{/if}
    {:else}
      <Linie werte={reihe.werte} farbe={m.farbe} flaeche={m.flaeche && f !== "1x1"} jetzt={reihe.jetzt} minmax={f === "3x1"} einheit={m.einheitVerlauf} />
    {/if}
  </div>
{/snippet}

{#if f === "1x1"}
  <KKopf titel={m.kurz} symbol="{m.symbol} entbehrlich-gross" />
  {#if m.art === "bewoelkung" && wert !== null}
    <div class="k-reihe mitte">
      {@render dicke("")}
      <div class="wolkenring ans-ende"><Ring {wert} max={100} farbe="--text-2" /></div>
    </div>
    {@render zeile("entbehrlich-gross")}
  {:else}
    <div class="oben">{@render dicke("")}</div>
    {@render zeile(m.art === "druck" || m.art === "regen_heute" ? "" : "entbehrlich")}
    <div class="klein">{@render verlaufFeld()}</div>
  {/if}
{:else}
  <KKopf titel={m.titel} symbol={m.symbol} rechts={f === "2x1" ? "24 Stunden" : "48 Stunden"} />
  <div class="k-reihe">
    <div class="k-block wertblock">
      {@render dicke("halb")}
      {@render zeile("")}
    </div>
    {@render verlaufFeld()}
  </div>
{/if}

<style>
  .oben {
    margin-top: 6px;
  }
  /* Kurzer Verlauf unter dem Wert füllt die Resthöhe der Kachel */
  .klein {
    flex: 1 1 0;
    min-height: 0;
    display: flex;
    margin-top: 4px;
  }
  /* Verlauf: Linie oder Säulen, darüber ein ehrlicher Hinweis, wenn nichts zu zeichnen ist */
  .verlauf {
    flex: 1 1 0;
    min-width: 0;
    min-height: 0;
    align-self: stretch;
    display: flex;
    position: relative;
  }
  /* Der Wertblock darf den Verlauf nicht verdrängen; lange Zusätze kürzen sich */
  .wertblock {
    max-width: 58%;
  }
  .wolkenring {
    flex: none;
    width: 34px;
    height: 34px;
    display: flex;
  }
</style>
