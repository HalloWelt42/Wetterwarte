<script lang="ts">
  // Blatt Pollen: Heute, Morgen und Übermorgen zum Umschalten, alle Arten mit Stufenpunkten und
  // Wort; die in der Kachel gewählten Allergien stehen oben.
  import type { KachelProps } from "../kachelprops";
  import type { Pollenart } from "../typen";
  import { einstellung } from "../../kern/gemeinsam";
  import { pollenPunkte, pollenWort } from "../format";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Segmente from "./bausteine/Segmente.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { erklaerung } from "./erklaerungen";

  let { kachel, daten, zone }: KachelProps = $props();

  type Tag = "heute" | "morgen" | "uebermorgen";
  const TAGE: { wert: Tag; titel: string }[] = [
    { wert: "heute", titel: "Heute" },
    { wert: "morgen", titel: "Morgen" },
    { wert: "uebermorgen", titel: "Übermorgen" },
  ];
  // Bäume, Gräser und Kräuter als Symbol
  const SYMBOL: Record<string, string> = {
    hasel: "fa-tree", erle: "fa-tree", esche: "fa-tree", birke: "fa-tree",
    graeser: "fa-seedling", roggen: "fa-seedling", beifuss: "fa-leaf", ambrosia: "fa-leaf",
  };

  let tag = $state<Tag>("heute");
  const pollen = $derived(daten.pollen);
  const bereich = $derived(daten.bereiche.pollen);
  const allergien = $derived(einstellung<string[]>("pollen", kachel.conf, "allergien") ?? []);
  const eigene = $derived(pollen ? pollen.arten.filter((a) => allergien.includes(a.schluessel)) : []);
  const weitere = $derived(pollen ? pollen.arten.filter((a) => !allergien.includes(a.schluessel)) : []);
  const staerkste = $derived(pollen ? [...pollen.arten].sort((a, b) => b[tag] - a[tag])[0] : undefined);
  const naechster = $derived<Tag | null>(tag === "heute" ? "morgen" : tag === "morgen" ? "uebermorgen" : null);
  const tagTitel = $derived(TAGE.find((t) => t.wert === tag)!.titel);
</script>

{#snippet art(a: Pollenart, hervor: boolean)}
  <div class="zeile">
    <span class="sym" class:hervor><i class="fa-solid {SYMBOL[a.schluessel] ?? 'fa-seedling'}"></i></span>
    <div class="haupt">
      <b>{a.titel}</b>
      {#if naechster}<small>{naechster === "morgen" ? "morgen" : "übermorgen"} {pollenWort(a[naechster])}</small>{/if}
    </div>
    <span class="rechts">
      <span class="punkte p{pollenPunkte(a[tag])}"><span></span><span></span><span></span></span>
      <span>{pollenWort(a[tag])}</span>
    </span>
  </div>
{/snippet}

{#if !pollen}
  <div class="abschnitt">
    {#if bereich.status === "fehlt"}
      <Hinweis titel="Pollendaten fehlen" text="Die Quelle für den Pollenflug antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    {:else}
      <Hinweis symbol="fa-seedling" titel="Keine Pollenvorhersage für diesen Ort" text="Die Vorhersage zum Pollenflug gibt es nur für Orte in Deutschland." />
    {/if}
    <Stand {bereich} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <Segmente optionen={TAGE} bind:wert={tag} />
    <p class="lage">
      {#if staerkste && staerkste[tag] >= 0.5}
        {tagTitel} am stärksten: <b>{staerkste.titel}</b>, {pollenWort(staerkste[tag])}.
      {:else}
        {tagTitel} fliegen nach der Vorhersage keine nennenswerten Pollen.
      {/if}
    </p>
    {#if eigene.length}
      <h3 class="unter-titel">Deine Allergien</h3>
      <div class="zeilen">{#each eigene as a (a.schluessel)}{@render art(a, true)}{/each}</div>
    {/if}
    {#if weitere.length}
      <h3 class="unter-titel">{eigene.length ? "Weitere" : "Alle Arten"}</h3>
      <div class="zeilen">{#each weitere as a (a.schluessel)}{@render art(a, false)}{/each}</div>
    {/if}
    <p>
      {#if eigene.length}Deine Allergien stehen oben.{:else}Allergien lassen sich am Rechner in der Pollen-Kachel wählen, sie stehen dann oben.{/if}
      Vorhersage für die Region {pollen.region}.
    </p>
    <Stand {bereich} {zone} />
  </div>

  <Begriffe liste={[erklaerung.pollenstufen]} />
{/if}

<style>
  /* Gemeinsame Regeln tragen den Vorsatz .tel; mit .tel davor gewinnt die eigene Regel */
  :global(.tel) .unter-titel {
    margin-top: 16px;
  }
  :global(.tel) .lage {
    font-size: var(--s17);
    color: var(--text);
    margin-bottom: 12px;
  }
  :global(.tel) .sym.hervor {
    color: var(--akzent);
  }
</style>
