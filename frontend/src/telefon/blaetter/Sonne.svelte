<script lang="ts">
  // Blatt Sonne: großer Sonnenbogen mit Restzeit, die Zeiten von heute (Auf- und Untergang,
  // Tageslänge mit Änderung zu morgen, Höchststand, goldene Stunde, Dämmerung) und die nächsten Tage.
  import type { KachelProps } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { minutenAmTag, uhrzeit } from "../../kern/zeit";
  import { zahl } from "../format";
  import Sonnenbogen from "../mikro/Sonnenbogen.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { dauerLang, kalendertag, tageZwischen, tagLang, tagNah, versatzMinuten } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { zusatzzeiten } from "./sonnenstand";

  let { daten, zone }: KachelProps = $props();

  const t = $derived(daten.tage[0] ?? null);
  const auf = $derived(t?.sonnenaufgang ?? null);
  const unter = $derived(t?.sonnenuntergang ?? null);
  const morgen = $derived(daten.tage[1] ?? null);
  const jetztMs = $derived(Math.floor(uhr.jetzt.getTime() / 60_000) * 60_000); // minütlich genügt
  const zusatz = $derived(t && auf && unter ? zusatzzeiten(t.datum, daten.ort.lat, auf, unter) : null);
  const aenderung = $derived(t && morgen ? morgen.tageslaenge_s - t.tageslaenge_s : null);
  const heute = $derived(kalendertag(daten.zeit, zone));

  // Kopfzeile der Tafel: Restzeit hell, Zeit bis Aufgang oder Hinweis auf morgen
  const lage = $derived.by(() => {
    if (!auf || !unter) return "";
    const a = new Date(auf).getTime();
    const u = new Date(unter).getTime();
    if (jetztMs < a) return `Aufgang in ${dauerLang((a - jetztMs) / 1000)}`;
    if (jetztMs < u) return `Noch ${dauerLang((u - jetztMs) / 1000)} hell`;
    return morgen?.sonnenaufgang ? `Untergegangen, morgen auf um ${uhrzeit(morgen.sonnenaufgang, zone)}` : "Die Sonne ist untergegangen";
  });

  // Stunden und Minuten getrennt für die große Anzeige der Tageslänge
  const laenge = (s: number) => ({ h: Math.floor(Math.round(s / 60) / 60), m: Math.round(s / 60) % 60 });

  function umstellung(i: number): boolean {
    const a = daten.tage[i - 1]?.sonnenaufgang;
    const b = daten.tage[i]?.sonnenaufgang;
    return !!a && !!b && versatzMinuten(a) !== versatzMinuten(b);
  }
  const tagName = (datum: string) => (tageZwischen(heute, datum) === 1 ? `Morgen, ${tagLang(datum)}` : tagLang(datum));
</script>

{#if !t}
  <div class="abschnitt">
    <Hinweis titel="Sonnenzeiten fehlen" text="Die Wetterquelle hat gerade keine Tage geliefert. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    {#if auf && unter}
      <div class="tafel">
        <div class="tafel-kopf"><b>{lage}</b><span>{tagNah(t.datum, heute) === "heute" ? "heute" : tagLang(t.datum)}</span></div>
        <div class="diagramm">
          <Sonnenbogen
            auf={minutenAmTag(auf, zone)}
            unter={minutenAmTag(unter, zone)}
            jetzt={minutenAmTag(new Date(jetztMs), zone)}
            beschriftung={[uhrzeit(auf, zone), uhrzeit(unter, zone)]}
          />
        </div>
      </div>
    {:else}
      <Hinweis
        symbol="fa-sun"
        titel="Kein Auf- oder Untergang"
        text={t.tageslaenge_s > 43_200 ? "Die Sonne geht heute nicht unter." : "Die Sonne geht heute nicht auf."}
      />
    {/if}
  </div>

  <div class="abschnitt">
    <h3>Heute</h3>
    <div class="werte-gitter">
      {#if auf && unter}
        <div class="wg"><div class="wg-kopf"><i class="fa-solid fa-arrow-up"></i>Aufgang</div><div class="wg-wert">{uhrzeit(auf, zone)}</div></div>
        <div class="wg"><div class="wg-kopf"><i class="fa-solid fa-arrow-down"></i>Untergang</div><div class="wg-wert">{uhrzeit(unter, zone)}</div></div>
      {/if}
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-clock"></i>Tageslänge</div>
        <div class="wg-wert">{laenge(t.tageslaenge_s).h}<small>Stunden</small> {laenge(t.tageslaenge_s).m}<small>Minuten</small></div>
        {#if aenderung !== null}
          <div class="wg-unter">
            {#if Math.abs(aenderung) < 30}morgen gleich lang{:else}morgen <b>{dauerLang(aenderung)}</b> {aenderung > 0 ? "länger" : "kürzer"}{/if}
          </div>
        {/if}
      </div>
      {#if zusatz}
        <div class="wg">
          <div class="wg-kopf"><i class="fa-solid fa-sun"></i>Höchststand</div>
          <div class="wg-wert">{uhrzeit(zusatz.mittag, zone)}</div>
          <div class="wg-unter">etwa {zahl(Math.max(0, zusatz.hoehe))}° über dem Horizont</div>
        </div>
        {#if zusatz.goldeneStunde}
          <div class="wg">
            <div class="wg-kopf"><i class="fa-solid fa-camera"></i>Goldene Stunde</div>
            <div class="wg-wert">{uhrzeit(zusatz.goldeneStunde, zone)}</div>
            <div class="wg-unter">bis zum Untergang</div>
          </div>
        {/if}
        {#if zusatz.daemmerungEnde}
          <div class="wg">
            <div class="wg-kopf"><i class="fa-solid fa-moon"></i>Dämmerung</div>
            <div class="wg-wert">{uhrzeit(zusatz.daemmerungEnde, zone)}</div>
            <div class="wg-unter">dann dunkel</div>
          </div>
        {/if}
      {/if}
    </div>
  </div>

  {#if daten.tage.length > 1}
    <div class="abschnitt">
      <h3>Nächste Tage · Aufgang und Untergang</h3>
      <div class="zeilen">
        {#each daten.tage.slice(1) as d, i (d.datum)}
          <div class="zeile">
            <div class="haupt">
              <b>{tagName(d.datum)}</b>
              <small>{dauerLang(d.tageslaenge_s)}{#if umstellung(i + 1)}{" "}· Zeitumstellung{/if}</small>
            </div>
            {#if d.sonnenaufgang && d.sonnenuntergang}
              <span class="rechts">
                <span class="zahl-r"><i class="fa-solid fa-arrow-up pfeil"></i>{uhrzeit(d.sonnenaufgang, zone)}</span>
                <span class="zahl-r"><i class="fa-solid fa-arrow-down pfeil"></i>{uhrzeit(d.sonnenuntergang, zone)}</span>
              </span>
            {:else}
              <span class="rechts">keine Angabe</span>
            {/if}
          </div>
        {/each}
      </div>
      <Stand bereich={daten.bereiche.basis} {zone} />
    </div>
  {/if}

  <Begriffe liste={[erklaerung.goldeneStunde, erklaerung.daemmerung]} />
{/if}

<style>
  .pfeil {
    font-size: var(--s13);
    color: var(--text-3);
    margin-right: 4px;
  }
</style>
