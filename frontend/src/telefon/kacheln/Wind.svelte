<script lang="ts">
  // Wind: 1x1 Wert mit kleiner Windrose in der Ecke, 2x1 Wert, Böen und Rose, Richtung im Kopf,
  // 2x2 große Rose, Wert, Böen, Stärke nach Beaufort und in Worten.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { beaufort, richtung, richtungLang, windWort, zahl } from "../format";
  import KKopf from "../KKopf.svelte";
  import Windrose from "../mikro/Windrose.svelte";

  let { kachel, daten }: KachelProps = $props();

  const f = $derived(form(kachel));
  const j = $derived(daten.jetzt);
</script>

{#if !j}
  <KKopf titel="Wind" symbol="fa-wind" />
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if f === "1x1"}
  <KKopf titel="Wind" symbol="fa-wind entbehrlich-gross" />
  <div class="rose-ecke"><Windrose grad={j.wind_grad} /></div>
  <div class="k-fuss">
    <div class="wert"><b>{zahl(j.wind)}</b><small>km/h</small></div>
    <div class="unter">Böen <b>{zahl(j.boeen)}</b><span class="entbehrlich">{" · "}{richtung(j.wind_grad)}</span></div>
  </div>
{:else if f === "2x1"}
  <KKopf titel="Wind" symbol="fa-wind" rechts="aus {richtungLang(j.wind_grad)}" />
  <div class="k-reihe">
    <div class="k-block">
      <div class="wert dick"><b>{zahl(j.wind)}</b><small>km/h</small></div>
      <div class="unter">Böen <b>{zahl(j.boeen)}</b> km/h</div>
    </div>
    <div class="rose-seite ans-ende"><Windrose grad={j.wind_grad} /></div>
  </div>
{:else}
  <KKopf titel="Wind" symbol="fa-wind" rechts="Stärke {beaufort(j.wind)}" />
  <div class="rose-gross"><Windrose grad={j.wind_grad} /></div>
  <div class="k-reihe fest">
    <div class="wert halb"><b>{zahl(j.wind)}</b><small>km/h</small></div>
    <div class="kz ans-ende boeen"><b>{zahl(j.boeen)} km/h</b><small>Böen</small></div>
  </div>
  <div class="unter umbruch">{windWort(j.wind)}, aus {richtungLang(j.wind_grad)}</div>
{/if}

<style>
  /* Kleine Rose oben rechts in der Ecke */
  .rose-ecke {
    position: absolute;
    right: 8px;
    top: 8px;
    width: 40px;
    height: 40px;
    display: flex;
  }
  /* Rose so hoch wie die Reihe, quadratisch */
  .rose-seite {
    flex: none;
    align-self: stretch;
    aspect-ratio: 1;
    display: flex;
  }
  /* Große Rose füllt die Mitte */
  .rose-gross {
    flex: 1 1 0;
    min-height: 0;
    display: flex;
    margin: 6px 0;
  }
  /* Stärke und Richtung dürfen auf zwei Zeilen umbrechen; die Rose wird dann kleiner */
  .unter.umbruch {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .boeen {
    text-align: right;
  }
</style>
