<script lang="ts">
  // Blitze der letzten 30 Minuten im eingestellten Umkreis (25, 50 oder 100 km): 1x1 Anzahl und
  // nächster Abstand, 2x1 zusätzlich Richtung, wann zuletzt und kleine Ringe, 2x2 große
  // Entfernungsringe mit den Einschlägen. Ohne Einschlag im Umkreis ruhig "Keine Blitze in der Nähe".
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { einstellung } from "../../kern/gemeinsam";
  import { uhr } from "../../kern/uhr.svelte";
  import { vorZeit } from "../../kern/zeit";
  import { richtungLang, zahl } from "../format";
  import KKopf from "../KKopf.svelte";
  import Ringe from "../mikro/Ringe.svelte";

  let { kachel, daten }: KachelProps = $props();

  const SYMBOL = "fa-bolt";
  // "in der Nähe" bleibt beisammen, damit der Satz zweizeilig sauber umbricht
  const RUHIG = "Keine Blitze in\u00a0der\u00a0Nähe";
  // Entfernungsringe je Umkreis (km)
  const RINGE: Record<number, number[]> = { 25: [10, 25], 50: [10, 25, 50], 100: [25, 50, 100] };

  const f = $derived(form(kachel));
  const umkreis = $derived.by(() => {
    const wert = Number(einstellung<string>("blitze", kachel.conf, "umkreis"));
    return Number.isFinite(wert) && wert > 0 ? wert : Number(einstellung<string>("blitze", {}, "umkreis"));
  });
  const blitze = $derived(daten.blitze);
  // Einschläge im Umkreis, neueste zuerst (wie geliefert)
  const nah = $derived((blitze?.einschlaege ?? []).filter((e) => e.km <= umkreis));
  const naechster = $derived(nah.reduce<(typeof nah)[number] | null>((n, e) => (!n || e.km < n.km ? e : n), null));
  // Die Liste ist gekürzt, wenn mehr eingeschlagen hat als geliefert wurde: dann "mindestens"
  const gekuerzt = $derived(!!blitze && blitze.anzahl_30 > blitze.einschlaege.length);
  const anzahl = $derived(`${nah.length}${gekuerzt ? "+" : ""}`);
  const zuletzt = $derived(vorZeit(nah[0]?.zeit ?? null, uhr.jetzt, true));
  const ringe = $derived(RINGE[umkreis] ?? [umkreis / 2, umkreis]);
  const km = (v: number) => zahl(v, v < 10 ? 1 : 0);
  // Je näher, desto kräftiger die Warnfarbe
  const farbe = (v: number) => (v < 10 ? "c-w3" : v < 25 ? "c-w2" : "c-w1");
  // Lage vom Ort aus: "im Westen", "im Südosten" (Himmelsrichtung im Dativ)
  const lage = (g: number) => `im ${richtungLang(g)}en`;
</script>

{#if !blitze}
  <KKopf titel="Blitze" symbol={SYMBOL} />
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if !naechster}
  {#if f === "1x1"}
    <KKopf titel="Blitze" symbol={SYMBOL} />
    <div class="k-fuss">
      <div class="titel-2">{RUHIG}</div>
    </div>
  {:else if f === "2x1"}
    <KKopf titel="Blitze" symbol={SYMBOL} rechts="Umkreis {umkreis} km" />
    <div class="k-reihe mitte">
      <div class="k-block dehnen"><div class="titel-2">{RUHIG}</div></div>
      <div class="ringe-quadrat"><Ringe punkte={[]} max={umkreis} {ringe} /></div>
    </div>
  {:else}
    <KKopf titel="Blitze" symbol={SYMBOL} rechts="Umkreis {umkreis} km" />
    <div class="ringe-gross"><Ringe punkte={[]} max={umkreis} {ringe} /></div>
    <div class="titel-2">{RUHIG}</div>
    <div class="unter entbehrlich-gross">in den letzten 30 Minuten</div>
  {/if}
{:else if f === "1x1"}
  <KKopf titel="Blitze" symbol={SYMBOL} />
  <div class="k-fuss">
    <div class="vor entbehrlich">nächster</div>
    <div class="wert {farbe(naechster.km)}"><b>{km(naechster.km)}</b><small>km</small></div>
    <div class="unter"><b>{anzahl}</b> in 30 Minuten</div>
  </div>
{:else if f === "2x1"}
  <KKopf titel="Blitze" symbol={SYMBOL} rechts={zuletzt} />
  <div class="k-reihe">
    <div class="k-block dehnen">
      <div class="vor entbehrlich"><b>{anzahl}</b> in 30 Minuten</div>
      <div class="wert halb {farbe(naechster.km)}"><b>{km(naechster.km)}</b><small>km</small></div>
      <div class="unter">{lage(naechster.grad)}</div>
    </div>
    <div class="ringe-quadrat"><Ringe punkte={nah} max={umkreis} {ringe} /></div>
  </div>
{:else}
  <KKopf titel="Blitze" symbol={SYMBOL} rechts="Umkreis {umkreis} km" />
  <div class="ringe-gross"><Ringe punkte={nah} max={umkreis} {ringe} /></div>
  <div class="k-reihe fest">
    <div class="wert halb {farbe(naechster.km)}"><b>{km(naechster.km)}</b><small>km</small></div>
    <div class="kz ans-ende rechtsbuendig"><b>{anzahl}</b><small>in 30 Minuten</small></div>
  </div>
  <div class="unter">{lage(naechster.grad)}, {zuletzt}</div>
{/if}

<style>
  .vor b {
    color: var(--text);
  }
  /* 2x1: Ringe quadratisch über die Höhe der Reihe */
  .ringe-quadrat {
    align-self: stretch;
    aspect-ratio: 1;
    flex: none;
    display: flex;
  }
  /* 2x2: Ringe füllen die Resthöhe */
  .ringe-gross {
    flex: 1;
    min-height: 0;
    display: flex;
    margin: 4px 0;
  }
  .rechtsbuendig {
    text-align: right;
  }
</style>
