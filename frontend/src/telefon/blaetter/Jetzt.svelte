<script lang="ts">
  // Blatt Jetzt: Temperatur groß mit Zustand, alle Kennzahlen als Gitter großer Werte, Begriffe.
  import type { KachelProps } from "../kachelprops";
  import { zustandText } from "../../kern/wetterbild";
  import { beaufort, grad, richtungLang, uvWort, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import { heute, regenAbText } from "../rechnen";
  import Symbol from "../Symbol.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { erklaerung } from "./erklaerungen";
  import { druckTendenz } from "../kacheln/messwerte";
  import { bewoelkungWort, feuchteWort, gefuehltSatz, sichtWort, taupunktWort, uvZahl } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const j = $derived(daten.jetzt);
  const tag = $derived(heute(daten));
  const boeenHeute = $derived(daten.tage[0]?.boeen_max ?? null);
  const tendenz = $derived(druckTendenz(j?.druck_tendenz ?? null));
  const regenText = $derived(regenAbText(daten));
</script>

{#if !j}
  <div class="abschnitt">
    <Hinweis titel="Aktuelle Werte fehlen" text="Die Wetterquelle antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <Symbol code={j.code} tag={j.tag} />
      <div class="held-text">
        <div class="riesen-zahl {tempKlasse(j.temp)}">{grad(j.temp)}</div>
        <div class="held-satz">{zustandText(j.code)}</div>
        <div class="held-unter">
          Gefühlt <b>{grad(j.gefuehlt)}</b>{#if tag}{" "}· Hoch <b>{grad(tag.hoch)}</b> · Tief <b>{grad(tag.tief)}</b>{/if}
        </div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Messwerte</h3>
    <div class="werte-gitter">
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-temperature-half"></i>Gefühlt</div>
        <div class="wg-wert {tempKlasse(j.gefuehlt)}">{grad(j.gefuehlt)}</div>
        <div class="wg-unter">{gefuehltSatz(j.temp, j.gefuehlt, j.wind)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-droplet"></i>Feuchte</div>
        <div class="wg-wert">{zahl(j.feuchte)}<small>%</small></div>
        <div class="wg-unter">{feuchteWort(j.feuchte)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-water"></i>Taupunkt</div>
        <div class="wg-wert">{grad(j.taupunkt)}</div>
        <div class="wg-unter">{taupunktWort(j.taupunkt)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-gauge"></i>Luftdruck</div>
        <div class="wg-wert">{zahl(j.druck)}<small>hPa</small></div>
        <div class="wg-unter">
          {#if tendenz && j.druck_tendenz != null}
            <i class="fa-solid {tendenz.pfeil}"></i> {tendenz.wort}, <b>{j.druck_tendenz > 0 ? "+" : ""}{zahl(j.druck_tendenz, 1)}</b> in 3 Stunden
          {:else}
            Tendenz unbekannt
          {/if}
        </div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-eye"></i>Sicht</div>
        {#if j.sicht_km !== null}
          <div class="wg-wert">{zahl(j.sicht_km, j.sicht_km < 10 ? 1 : 0)}<small>km</small></div>
          <div class="wg-unter">{sichtWort(j.sicht_km)}</div>
        {:else}
          <div class="wg-wert leer">keine Angabe</div>
        {/if}
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-cloud"></i>Bewölkung</div>
        <div class="wg-wert">{zahl(j.bewoelkung)}<small>%</small></div>
        <div class="wg-unter">{bewoelkungWort(j.bewoelkung)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-wind"></i>Wind</div>
        <div class="wg-wert">{zahl(j.wind)}<small>km/h</small></div>
        <div class="wg-unter">aus {richtungLang(j.wind_grad)}, Stärke {beaufort(j.wind)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-wind"></i>Böen</div>
        <div class="wg-wert">{zahl(j.boeen)}<small>km/h</small></div>
        <div class="wg-unter">{#if boeenHeute !== null}heute bis <b>{zahl(boeenHeute)}</b>{:else}Stärke {beaufort(j.boeen)}{/if}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-sun"></i>UV-Index</div>
        <div class="wg-wert">{uvZahl(j.uv)}</div>
        <div class="wg-unter">{uvWort(j.uv)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-umbrella"></i>Regen jetzt</div>
        <div class="wg-wert">{zahl(j.regen_mm, j.regen_mm > 0 && j.regen_mm < 10 ? 1 : 0)}<small>mm</small></div>
        <div class="wg-unter">{j.regen_mm > 0 ? "es regnet" : regenText || "trocken in den nächsten 24 Stunden"}</div>
      </div>
    </div>
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>

  <Begriffe liste={[erklaerung.gefuehlt, erklaerung.taupunkt, erklaerung.luftdruck, erklaerung.sicht, erklaerung.boeen, erklaerung.uv]} />
{/if}

