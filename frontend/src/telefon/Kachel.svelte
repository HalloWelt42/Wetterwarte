<script lang="ts">
  // Hülle einer Telefon-Kachel: Lage im Raster, Tippen öffnet das Detailblatt (Regenradar: den
  // Karten-Reiter). Die Kachel selbst wird erst mit echten Daten gezeichnet; fehlt ein Bereich,
  // den sie braucht, steht ein ehrlicher Hinweis da, ist er alt, eine Altersmarke.
  import type { TelefonKachel } from "../kern/gemeinsam";
  import { telefonKatalog } from "../kern/gemeinsam";
  import { uhr } from "../kern/uhr.svelte";
  import { vorZeit } from "../kern/zeit";
  import { telefonTypen } from "./katalog";
  import { oeffne, zeige } from "./ansicht.svelte";
  import KKopf from "./KKopf.svelte";
  import type { OrtStand } from "./wetter.svelte";

  let { kachel, stand }: { kachel: TelefonKachel; stand: OrtStand } = $props();

  const typ = $derived(telefonTypen[kachel.typ]);
  const def = $derived(telefonKatalog.typen[kachel.typ]);
  const daten = $derived(stand.daten);
  const bereiche = $derived(typ?.bereiche ?? []);
  const fehlt = $derived(!!daten && bereiche.some((b) => daten.bereiche[b].status === "fehlt"));
  const altStand = $derived.by(() => {
    if (!daten) return null;
    const alt = bereiche.filter((b) => daten.bereiche[b].status === "alt").map((b) => daten.bereiche[b].stand);
    if (stand.zustand === "alt") alt.push(new Date(stand.geholt).toISOString());
    return alt.filter((s): s is string => !!s).sort()[0] ?? null;
  });

  function tippen(): void {
    if (typ?.ziel === "karte") zeige("karte");
    else oeffne({ art: "detail", kachel });
  }
</script>

<div
  class="k"
  style="--x: {kachel.x}; --y: {kachel.y}; --w: {kachel.w}; --h: {kachel.h}"
  role="button"
  tabindex="0"
  aria-label={def?.titel ?? kachel.typ}
  onclick={tippen}
  onkeydown={(e) => (e.key === "Enter" || e.key === " ") && tippen()}
>
  {#if !typ || !def}
    <KKopf titel={kachel.typ} />
  {:else if !daten}
    <KKopf titel={def.titel} symbol={def.symbol} />
    <div class="k-mitte" aria-busy="true">
      <span class="sk" style="height: 34%; width: 62%"></span>
      <span class="sk" style="height: 14%; width: 82%; margin-top: 8px"></span>
    </div>
  {:else if fehlt}
    <KKopf titel={def.titel} symbol={kachel.w > 1 ? def.symbol : ""} />
    <div class="k-mitte fehlt-hinweis">
      <i class="fa-solid fa-plug-circle-xmark"></i>
      <div class="k-hinweis">{typ.fehltHinweis ?? "Gerade nicht erreichbar"}</div>
    </div>
  {:else}
    <typ.komponente {kachel} {daten} zone={daten.ort.zeitzone} />
    {#if altStand}<span class="k-alter">{vorZeit(altStand, uhr.jetzt, true)}</span>{/if}
  {/if}
</div>

<style>
  .fehlt-hinweis {
    align-items: flex-start;
    gap: 6px;
  }
  .fehlt-hinweis i {
    color: var(--text-3);
    font-size: var(--s19);
  }
</style>
