<script lang="ts">
  // Eine Kachelseite (Wetter oder Gesundheit): Kopf, auf der Wetterseite das Warnband (wenn dort
  // keine Warnkachel steht), dann das Raster des Telefon-Layouts. Waagerecht wischen wechselt die Seite.
  import { orteState } from "../kern/orte.svelte";
  import { telefonKatalog } from "../kern/gemeinsam";
  import { ansicht, wischeSeite } from "./ansicht.svelte";
  import { aktivesProfil, profile } from "./profil.svelte";
  import { standVon } from "./wetter.svelte";
  import { wischen } from "./wischen";
  import Kachel from "./Kachel.svelte";
  import Kopf from "./Kopf.svelte";
  import Warnband from "./Warnband.svelte";

  let { seite }: { seite: string } = $props();

  const kacheln = $derived(aktivesProfil()?.telefon?.seiten[seite] ?? []);
  const reihen = $derived(Math.max(0, ...kacheln.map((k) => k.y + k.h)));
  const stand = $derived(standVon(ansicht.ort));
  const mitWarnband = $derived(seite === "wetter" && !kacheln.some((k) => k.typ === "warnungen"));
  const titel = $derived(telefonKatalog.seiten.find((s) => s.schluessel === seite)?.titel ?? "");
</script>

<div class="rollfeld" use:wischen={{ links: () => wischeSeite(1), rechts: () => wischeSeite(-1) }}>
  <Kopf />
  {#if mitWarnband && stand.daten}<Warnband daten={stand.daten} />{/if}
  {#if !orteState.liste.length && profile.geladen}
    <div class="seite-leer">
      <i class="fa-solid fa-location-dot"></i>
      <p>Noch kein Ort angelegt. Tippe oben auf den Namen, um einen Ort zu suchen.</p>
    </div>
  {:else if profile.geladen && !kacheln.length}
    <div class="seite-leer">
      <i class="fa-solid fa-table-cells-large"></i>
      <p>Die Seite {titel} hat in diesem Profil keine Kacheln. Eingerichtet wird sie am Rechner in der Layout-Verwaltung.</p>
    </div>
  {:else}
    <main class="raster" style="grid-template-rows: repeat({reihen}, var(--feld))" aria-label={titel}>
      {#each kacheln as kachel (kachel.id)}
        <Kachel {kachel} {stand} />
      {/each}
    </main>
  {/if}
</div>

<style>
  .seite-leer {
    margin: 40px 24px;
    text-align: center;
    color: var(--text-2);
  }
  .seite-leer i {
    font-size: 34px;
    color: var(--text-3);
  }
  .seite-leer p {
    margin: 12px 0 0;
    line-height: 1.4;
  }
</style>
