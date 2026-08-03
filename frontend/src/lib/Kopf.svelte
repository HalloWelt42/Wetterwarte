<script lang="ts">
  import { meteocon } from "./icons";
  import { thema, themaUmschalten } from "./thema.svelte";
  import { ui } from "./ui.svelte";
  import { layoutState, setzeAktiv, profilIcon } from "./layout.svelte";
  import { hilfe } from "./hilfeStore.svelte";
  import KopfSuche from "./KopfSuche.svelte";

</script>

<header class="kopf">
  <button class="icon-knopf nur-mobil" title="Menü" aria-label="Menü öffnen" onclick={() => (ui.menu = true)}><i class="fa-solid fa-bars"></i></button>
  <div class="marke"><img class="mc" src={meteocon("partly-cloudy-day")} alt="" /> <span class="marke-txt">Wetterwarte</span></div>
  <KopfSuche />
  <div class="layout-tabs">
    {#each layoutState.liste as l}
      <button class:aktiv={layoutState.aktivId === l.id} onclick={() => setzeAktiv(l.id)}>
        <i class="fa-solid {profilIcon(l)}"></i>
        {l.name}
      </button>
    {/each}
    <button class="still" title="Neues Layout" onclick={() => (ui.layouts = true)}><i class="fa-solid fa-plus"></i></button>
  </div>
  <div class="kopf-rechts">
    <button class="knopf primaer" onclick={() => (ui.katalog = true)}><i class="fa-solid fa-plus"></i> <span class="nur-desktop-inline">Kachel</span></button>
    <button class="icon-knopf" title={thema.wert === "hell" ? "Zu Dunkel wechseln" : "Zu Hell wechseln"} aria-label="Hell/Dunkel umschalten" onclick={themaUmschalten}>
      <i class="fa-solid fa-circle-half-stroke" style="font-size: 1.05rem; transform: rotate({thema.wert === 'hell' ? 0 : 180}deg); transition: transform var(--schnell)"></i>
    </button>
    <button class="icon-knopf nur-desktop" title="System & Dienste" onclick={() => (ui.dienste = true)} aria-label="System und Dienste"><i class="fa-solid fa-gear"></i></button>
    <button class="icon-knopf nur-desktop" title="Erste Schritte" onclick={() => (ui.willkommen = true)} aria-label="Erste Schritte"><i class="fa-solid fa-life-ring"></i></button>
    <button class="icon-knopf nur-desktop" title="Hilfe" onclick={() => hilfe.toggle("uebersicht")}><i class="fa-solid fa-circle-question"></i></button>
    <button class="icon-knopf spendenherz" title="Danke sagen" onclick={() => (ui.spende = true)} aria-label="Danke sagen"><i class="fa-solid fa-heart"></i></button>
  </div>
</header>
