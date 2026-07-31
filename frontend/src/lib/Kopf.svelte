<script lang="ts">
  import { meteocon } from "./icons";
  import { thema, themaUmschalten } from "./thema.svelte";
  import { ui } from "./ui.svelte";
  import { layoutState, setzeAktiv } from "./layout.svelte";
  import { hilfe } from "./hilfeStore.svelte";

  const iconMap: Record<string, string> = {
    Zuhause: "fa-house",
    Garten: "fa-seedling",
    Reise: "fa-suitcase-rolling",
    Unwetter: "fa-triangle-exclamation",
  };
  function iconFuer(name: string): string {
    return iconMap[name] ?? "fa-table-cells-large";
  }
</script>

<header class="kopf">
  <div class="marke"><img class="mc" src={meteocon("partly-cloudy-day")} alt="" /> Wetterwarte</div>
  <div class="kopf-suche">
    <i class="fa-solid fa-magnifying-glass"></i>
    <input
      type="text"
      placeholder="Ort suchen ..."
      readonly
      onclick={() => (ui.ortssuche = true)}
      onfocus={() => (ui.ortssuche = true)}
    />
  </div>
  <div class="layout-tabs">
    {#each layoutState.liste as l}
      <button class:aktiv={layoutState.aktivId === l.id} onclick={() => setzeAktiv(l.id)}>
        <i class="fa-solid {iconFuer(l.name)}"></i>
        {l.name}
      </button>
    {/each}
    <button class="still" title="Neues Layout" onclick={() => (ui.layouts = true)}><i class="fa-solid fa-plus"></i></button>
  </div>
  <div class="kopf-rechts">
    <button class="knopf primaer" onclick={() => (ui.katalog = true)}><i class="fa-solid fa-plus"></i> Kachel</button>
    <button class="icon-knopf" title="Erscheinungsbild" onclick={themaUmschalten}>
      <i class="fa-solid {thema.wert === 'hell' ? 'fa-moon' : 'fa-sun'}"></i>
    </button>
    <button class="icon-knopf" title="System & Dienste" onclick={() => (ui.dienste = true)} aria-label="System und Dienste"><i class="fa-solid fa-gear"></i></button>
    <button class="icon-knopf" title="Hilfe" onclick={() => hilfe.toggle("uebersicht")}><i class="fa-solid fa-circle-question"></i></button>
  </div>
</header>
