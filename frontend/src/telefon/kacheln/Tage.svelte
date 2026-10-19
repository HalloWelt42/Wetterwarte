<script lang="ts">
  // Tage: 1x1 morgen, 1x3 fünf Tage schmal, 2x2 vier Tage ohne Band, 3x2 fünf Tage mit Band,
  // 3x3 sieben Tage mit Band und Regen. Band über die Spanne der gezeigten Tage, Jetzt-Marke heute.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { grad, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import KKopf from "../KKopf.svelte";
  import Symbol from "../Symbol.svelte";

  let { kachel, daten }: KachelProps = $props();

  const f = $derived(form(kachel));
  const anzahl = $derived(f === "1x1" ? 2 : f === "2x2" ? 4 : f === "3x3" ? 7 : 5);
  const tage = $derived(daten.tage.slice(0, anzahl));
  const lo = $derived(Math.min(...tage.map((t) => t.tief)));
  const hi = $derived(Math.max(...tage.map((t) => t.hoch)));
  const spanne = $derived(hi - lo || 1);
  const links = (t: number) => ((t - lo) / spanne) * 100;
  const jetzt = $derived(daten.jetzt?.temp ?? null);
  const morgen = $derived(daten.tage[1]);

  function name(i: number): string {
    if (i === 0) return "Heute";
    const d = new Date(`${tage[i].datum}T12:00:00`);
    return ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"][d.getDay()];
  }
  // Letzte Zeile darf bei großer Schrift wegfallen
  const entbehrlich = (i: number) => i === tage.length - 1 && tage.length > 3;
</script>

{#if f === "1x1" && morgen}
  <KKopf titel="Morgen" />
  <Symbol code={morgen.code} klasse="mc-ecke klein" />
  <div class="k-fuss">
    <div class="wert dick {tempKlasse(morgen.hoch)}"><b>{grad(morgen.hoch)}</b><small>/{grad(morgen.tief)}</small></div>
    <div class="unter"><i class="fa-solid fa-umbrella c-regen"></i> <b>{zahl(morgen.regen_wahrsch ?? 0)} %</b></div>
  </div>
{:else if f === "1x3"}
  <KKopf titel="{tage.length} Tage" />
  <div class="tage-schmal">
    {#each tage as t, i}
      <div class:entbehrlich={entbehrlich(i)}>
        <div class="ts-tag">{name(i)}</div>
        <div class="ts-zeile"><Symbol code={t.code} /><b class={tempKlasse(t.hoch)}>{grad(t.hoch)}</b><small class="entbehrlich">{grad(t.tief)}</small></div>
      </div>
    {/each}
  </div>
{:else if f === "2x2"}
  <KKopf titel="{tage.length} Tage" />
  <div class="tage">
    {#each tage as t, i}
      <div class="tz vier">
        <span class="tag">{name(i)}</span><Symbol code={t.code} />
        <span class="regen entbehrlich">{(t.regen_wahrsch ?? 0) >= 20 ? `${zahl(t.regen_wahrsch ?? 0)} %` : ""}</span>
        <span class="lo">{grad(t.tief)}</span><span class="hi">{grad(t.hoch)}</span>
      </div>
    {/each}
  </div>
{:else}
  <KKopf titel="{tage.length} Tage" rechts="{grad(lo)} bis {grad(hi)}" />
  <div class="tage">
    {#each tage as t, i}
      <div class="tz" class:mit-regen={f === "3x3"} class:entbehrlich={entbehrlich(i)}>
        <span class="tag">{name(i)}</span><Symbol code={t.code} />
        {#if f === "3x3"}<span class="regen">{(t.regen_wahrsch ?? 0) >= 10 ? `${zahl(t.regen_wahrsch ?? 0)} %` : ""}</span>{/if}
        <span class="lo">{grad(t.tief)}</span>
        <span class="band">
          <span style="left: {links(t.tief)}%; right: {100 - links(t.hoch)}%"></span>
          {#if i === 0 && jetzt !== null}<i style="left: {Math.min(100, Math.max(0, links(jetzt)))}%"></i>{/if}
        </span>
        <span class="hi">{grad(t.hoch)}</span>
      </div>
    {/each}
  </div>
{/if}
