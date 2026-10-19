<script lang="ts">
  // Sonne: Sonnenbogen mit dem Stand jetzt (Minuten in Ortszeit). 1x1 nächstes Ereignis (Untergang
  // oder Aufgang) mit kleinem Bogen, 2x1 Bogen mit Auf- und Untergang und der Zeit bis zum nächsten
  // Ereignis, 3x1 zusätzlich Tageslänge und Änderung zu morgen.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { minutenAmTag, uhrzeit } from "../../kern/zeit";
  import { dauer } from "../format";
  import KKopf from "../KKopf.svelte";
  import Sonnenbogen from "../mikro/Sonnenbogen.svelte";
  import { naechstesSonnenereignis, sekundenBis } from "./tageslauf";

  let { kachel, daten, zone }: KachelProps = $props();

  const f = $derived(form(kachel));
  const heute = $derived(daten.tage[0]);
  const bogen = $derived.by(() => {
    if (!heute?.sonnenaufgang || !heute.sonnenuntergang) return null;
    return {
      auf: minutenAmTag(heute.sonnenaufgang, zone),
      unter: minutenAmTag(heute.sonnenuntergang, zone),
      beschriftung: [uhrzeit(heute.sonnenaufgang, zone), uhrzeit(heute.sonnenuntergang, zone)] as [string, string],
    };
  });
  const jetzt = $derived(minutenAmTag(uhr.jetzt, zone));
  const naechstes = $derived(naechstesSonnenereignis(daten, uhr.jetzt));
  const rest = $derived(naechstes ? dauer(sekundenBis(naechstes.zeit, uhr.jetzt)) : "");
  // Änderung der Tageslänge von heute zu morgen in ganzen Minuten
  const aenderung = $derived.by(() => {
    const morgen = daten.tage[1];
    if (!heute || !morgen) return null;
    const min = Math.round((morgen.tageslaenge_s - heute.tageslaenge_s) / 60);
    if (min === 0) return { zahl: "", text: "morgen gleich lang" };
    return { zahl: `${Math.abs(min)} ${Math.abs(min) === 1 ? "Minute" : "Minuten"}`, text: min > 0 ? "länger" : "kürzer" };
  });
</script>

{#snippet bogenMitRest()}
  <div class="bogen-feld">
    {#if bogen}
      <Sonnenbogen auf={bogen.auf} unter={bogen.unter} {jetzt} beschriftung={bogen.beschriftung} />
      {#if naechstes}
        <div class="im-bogen"><small>{naechstes.art === "unter" ? "noch" : "Aufgang in"}</small><b>{rest}</b></div>
      {/if}
    {/if}
  </div>
{/snippet}

<KKopf titel="Sonne" symbol="fa-sun" />
{#if !bogen}
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if f === "1x1"}
  <div class="bogen-klein"><Sonnenbogen auf={bogen.auf} unter={bogen.unter} {jetzt} /></div>
  {#if naechstes}
    <div class="wert"><b>{uhrzeit(naechstes.zeit, zone)}</b></div>
    <div class="unter">{naechstes.art === "unter" ? "Untergang" : "Aufgang"}</div>
  {/if}
{:else if f === "2x1"}
  {@render bogenMitRest()}
{:else}
  <div class="k-reihe">
    {@render bogenMitRest()}
    <div class="k-block laenge">
      <div class="kz"><b class="gross">{dauer(heute.tageslaenge_s)}</b><small>Tageslänge</small></div>
      {#if aenderung}
        <div class="unter entbehrlich">
          {#if aenderung.zahl}morgen <b>{aenderung.zahl}</b> {aenderung.text}{:else}{aenderung.text}{/if}
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Kleiner Bogen über dem nächsten Ereignis */
  .bogen-klein {
    flex: 1 1 0;
    min-height: 0;
    display: flex;
    margin: 2px 0;
  }
  /* Bogen mit Beschriftung; die Restzeit steht darin */
  .bogen-feld {
    flex: 1 1 0;
    min-width: 0;
    min-height: 0;
    align-self: stretch;
    display: flex;
    position: relative;
    margin-top: 2px;
  }
  .laenge {
    padding-bottom: 2px;
  }
</style>
