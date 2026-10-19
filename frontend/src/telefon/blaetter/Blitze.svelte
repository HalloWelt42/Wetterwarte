<script lang="ts">
  // Blatt Blitze: Entfernungsringe groß im eingestellten Umkreis, Anzahl in 30 und 60 Minuten,
  // der nächste Einschlag und die Liste der letzten Einschläge mit Abstand, Richtung und Zeit.
  import type { KachelProps } from "../kachelprops";
  import { einstellung } from "../../kern/gemeinsam";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { richtungLang, zahl } from "../format";
  import Ringe from "../mikro/Ringe.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { vorLang } from "./datum";
  import { erklaerung } from "./erklaerungen";

  let { kachel, daten, zone }: KachelProps = $props();

  const LISTE_MAX = 30;
  const b = $derived(daten.blitze);
  const bereich = $derived(daten.bereiche.blitze);
  const umkreis = $derived(Number(einstellung<string>("blitze", kachel.conf, "umkreis")) || 50);
  const ringe = $derived(umkreis <= 25 ? [5, 10, 25] : umkreis <= 50 ? [10, 25, 50] : [25, 50, 100]);
  const imUmkreis = $derived(b ? b.einschlaege.filter((e) => e.km <= umkreis) : []);
  const km = (v: number) => zahl(v, v < 10 ? 1 : 0);
</script>

{#if !b}
  <div class="abschnitt">
    {#if bereich.status === "fehlt"}
      <Hinweis titel="Blitzdaten fehlen" text="Die Blitzquelle antwortet gerade nicht. Ob es blitzt, lässt sich gerade nicht sagen." />
    {:else}
      <Hinweis symbol="fa-bolt" titel="Keine Blitzdaten für diesen Ort" />
    {/if}
    <Stand {bereich} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="tafel">
      <div class="tafel-kopf">
        <b>{imUmkreis.length === 1 ? "1 Einschlag" : `${imUmkreis.length} Einschläge`} im Umkreis</b>
        <span>{umkreis} km · letzte 30 Minuten</span>
      </div>
      <div class="ringe-feld">
        <Ringe punkte={imUmkreis} max={umkreis} {ringe} />
      </div>
      <div class="tafel-fuss">Ringe bei {ringe.join(", ")} km, Norden oben. Die drei neuesten Einschläge leuchten heller.</div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Anzahl</h3>
    <div class="werte-gitter">
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-bolt"></i>30 Minuten</div>
        <div class="wg-wert">{zahl(b.anzahl_30)}</div>
        <div class="wg-unter">im ganzen Messgebiet</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-bolt"></i>60 Minuten</div>
        <div class="wg-wert">{zahl(b.anzahl_60)}</div>
        <div class="wg-unter">im ganzen Messgebiet</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-location-crosshairs"></i>Nächster</div>
        {#if b.naechster_km !== null}
          <div class="wg-wert">{km(b.naechster_km)}<small>km</small></div>
          <div class="wg-unter">{b.naechster_grad !== null ? `im ${richtungLang(b.naechster_grad)}en` : "Richtung unbekannt"}</div>
        {:else}
          <div class="wg-wert leer">keiner</div>
          <div class="wg-unter">in den letzten 30 Minuten</div>
        {/if}
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-clock"></i>Zuletzt</div>
        {#if b.zuletzt}
          <div class="wg-wert">{uhrzeit(b.zuletzt, zone)}</div>
          <div class="wg-unter">{vorLang(b.zuletzt, uhr.jetzt)}</div>
        {:else}
          <div class="wg-wert leer">keiner</div>
          <div class="wg-unter">in der letzten Stunde</div>
        {/if}
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Letzte Einschläge · neueste zuerst</h3>
    {#if b.einschlaege.length}
      <div class="zeilen">
        {#each b.einschlaege.slice(0, LISTE_MAX) as e, i (i)}
          <div class="zeile">
            <span class="sym" class:nah={e.km <= umkreis}><i class="fa-solid fa-bolt"></i></span>
            <div class="haupt"><b>{km(e.km)} km im {richtungLang(e.grad)}en</b><small>{vorLang(e.zeit, uhr.jetzt)}</small></div>
            <span class="rechts"><span class="zahl-r">{uhrzeit(e.zeit, zone)}</span></span>
          </div>
        {/each}
      </div>
      {#if b.einschlaege.length > LISTE_MAX}<p>Gezeigt sind die {LISTE_MAX} neuesten von {b.einschlaege.length} Einschlägen der letzten 30 Minuten.</p>{/if}
    {:else}
      <Hinweis symbol="fa-cloud" titel="Keine Einschläge" text="In den letzten 30 Minuten hat es im Messgebiet nicht geblitzt." />
    {/if}
    <Stand {bereich} {zone} />
  </div>

  <Begriffe liste={[erklaerung.blitzUmkreis]} />
{/if}

<style>
  .ringe-feld {
    position: relative;
    width: 100%;
    max-width: 320px;
    aspect-ratio: 1;
    margin: 0 auto;
  }
  :global(.tel) .sym.nah {
    color: var(--w1);
  }
</style>
