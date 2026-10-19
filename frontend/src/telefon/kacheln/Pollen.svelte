<script lang="ts">
  // Pollen: gewählte Allergien (Einstellung "allergien") zuerst und hervorgehoben, sonst nach Stärke.
  // 1x1 stärkste Art mit Stufenpunkten, 2x1 zwei, 2x2 vier, 1x3 bis sieben schmal, 3x2 sechs und 3x3
  // alle mit heute (Punkte und Wort) und morgen (Punkte). Ohne Pollendaten (Ort außerhalb
  // Deutschlands) ein ehrlicher Hinweis.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { einstellung } from "../../kern/gemeinsam";
  import { pollenPunkte, pollenWortKurz } from "../format";
  import type { Pollenart } from "../typen";
  import KKopf from "../KKopf.svelte";

  let { kachel, daten }: KachelProps = $props();

  const f = $derived(form(kachel));
  const allergien = $derived(einstellung<string[]>("pollen", kachel.conf, "allergien") ?? []);
  const arten = $derived(
    [...(daten.pollen?.arten ?? [])]
      .map((a) => ({ ...a, allergie: allergien.includes(a.schluessel) }))
      .sort((a, b) => Number(b.allergie) - Number(a.allergie) || b.heute - a.heute),
  );
  const anzahl = $derived(f === "2x1" ? 2 : f === "2x2" ? 4 : f === "1x3" ? 7 : f === "3x2" ? 6 : arten.length);
  const zeilen = $derived(arten.slice(0, anzahl));
  const erste = $derived(arten[0]);
  const weitere = $derived(arten.slice(1).filter((a) => pollenPunkte(a.heute) > 0).length);
  // Ohne Allergien und ohne Flug zeigt 1x1 keine beliebige Art, sondern den Satz
  const ruhig = $derived(!!erste && !erste.allergie && pollenPunkte(erste.heute) === 0);
  // Letzte Zeilen fallen bei großer Schrift zuerst weg
  const entbehrlich = (i: number) => anzahl > 4 && i === zeilen.length - 1;
  const entbehrlichGross = (i: number) => f === "3x2" && i === zeilen.length - 2;
</script>

{#snippet punkte(stufe: number)}
  <span class="punkte p{pollenPunkte(stufe)}"><span></span><span></span><span></span></span>
{/snippet}

{#snippet art(a: Pollenart & { allergie: boolean })}
  {#if a.allergie}<i class="fa-solid fa-hand-dots"></i>{/if}{a.titel}
{/snippet}

{#if !daten.pollen}
  <KKopf titel="Pollen" symbol="fa-seedling" />
  <div class="k-mitte"><div class="k-hinweis drei">Pollenflug nur für Deutschland</div></div>
{:else if !erste}
  <KKopf titel="Pollen" symbol="fa-seedling" />
  <div class="k-mitte"><div class="k-hinweis">keine Angabe</div></div>
{:else if f === "1x1"}
  <KKopf titel="Pollen" symbol="fa-seedling" />
  <div class="k-fuss">
    {#if ruhig}
      <div class="titel-2">kein Pollenflug</div>
      <div class="unter">heute</div>
    {:else}
      <div class="zustand">{#if erste.allergie}<i class="fa-solid fa-hand-dots allergie-zeichen"></i>{" "}{/if}{erste.titel}</div>
      <!-- In der Kachel das kurze Wort (ein Wort je Stufe), das Blatt nennt die Zwischenstufen aus -->
      <div class="stufe-zeile">{@render punkte(erste.heute)}<span class="unter">{pollenWortKurz(erste.heute)}</span></div>
      <div class="unter entbehrlich-gross">{weitere ? `dazu ${weitere} weitere` : "sonst keine"}</div>
    {/if}
  </div>
{:else if f === "1x3"}
  <KKopf titel="Pollen" symbol="fa-seedling" />
  <div class="pollen-schmal">
    {#each zeilen as a, i (a.schluessel)}
      <div class="ps" class:allergie={a.allergie} class:entbehrlich={entbehrlich(i)}>
        <span class="art">{@render art(a)}</span>{@render punkte(a.heute)}
      </div>
    {/each}
  </div>
{:else if f === "2x1" || f === "2x2"}
  <KKopf titel="Pollen" symbol="fa-seedling" rechts="heute" />
  <div class="zeilen-k">
    {#each zeilen as a (a.schluessel)}
      <div class="zk" class:allergie={a.allergie}>
        <span class="art">{@render art(a)}</span>
        <span class="zk-rechts">
          {@render punkte(a.heute)}<span class="stufe" class:matt={pollenPunkte(a.heute) === 0}>{pollenWortKurz(a.heute)}</span>
        </span>
      </div>
    {/each}
  </div>
{:else}
  <KKopf titel="Pollen" symbol="fa-seedling" rechts={daten.pollen.region} />
  <div class="tabelle">
    <div class="tz-kopf"><span></span><span>heute</span><span>morgen</span></div>
    {#each zeilen as a, i (a.schluessel)}
      <div class="tz-zeile" class:allergie={a.allergie} class:entbehrlich={entbehrlich(i)} class:entbehrlich-gross={entbehrlichGross(i)}>
        <span class="art">{@render art(a)}</span>
        <span class="tag">{@render punkte(a.heute)}<span class="stufe" class:matt={pollenPunkte(a.heute) === 0}>{pollenWortKurz(a.heute)}</span></span>
        <span class="morgen">{@render punkte(a.morgen)}</span>
      </div>
    {/each}
  </div>
{/if}

<style>
  /* In schmalen Kacheln braucht der Hinweis drei Zeilen; die Schrift wächst nur, solange
     "Deutschland" in die Breite passt */
  .k-hinweis.drei {
    -webkit-line-clamp: 3;
    line-clamp: 3;
    font-size: min(var(--s15), 16cqi);
  }
  .allergie-zeichen {
    font-size: 0.8em;
    color: var(--akzent);
  }
  .stufe-zeile {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
  }
  .stufe-zeile .unter {
    margin: 0;
  }
  /* Heute und morgen nebeneinander (3x2, 3x3) */
  .tabelle {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    flex: 1;
    min-height: 0;
  }
  .tz-kopf,
  .tz-zeile {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.6fr) auto;
    align-items: center;
    gap: 8px;
  }
  .tz-kopf {
    font-size: var(--s13);
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-3);
    line-height: 1.1;
  }
  .tz-kopf span:last-child,
  .morgen {
    justify-self: end;
  }
  .tz-zeile.allergie {
    margin: 0 -6px;
    padding: 3px 6px;
    border-radius: 10px;
    background: var(--flaeche-2);
  }
  .art {
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .tz-zeile.allergie .art {
    color: var(--text);
    font-weight: 700;
  }
  .tz-zeile .art i {
    margin-right: 5px;
    font-size: 0.85em;
    color: var(--akzent);
  }
  .tag {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
  }
  .stufe {
    font-size: var(--s15);
    color: var(--text-2);
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 0;
  }
  .stufe.matt {
    color: var(--text-3);
  }
</style>
