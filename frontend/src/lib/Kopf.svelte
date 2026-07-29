<script lang="ts">
  import { meteocon } from "./icons";
  import { thema, themaUmschalten } from "./thema.svelte";
  import { ui } from "./ui.svelte";

  const layouts = [
    { name: "Zuhause", icon: "fa-house" },
    { name: "Garten", icon: "fa-seedling" },
    { name: "Reise", icon: "fa-suitcase-rolling" },
    { name: "Unwetter", icon: "fa-triangle-exclamation" },
  ];
  let aktiv = $state("Zuhause");
</script>

<header class="kopf">
  <div class="marke"><img class="mc" src={meteocon("partly-cloudy-day")} alt="" /> Wetterwarte</div>
  <div class="kopf-suche">
    <i class="fa-solid fa-magnifying-glass"></i>
    <input type="text" placeholder="Ort suchen ..." />
  </div>
  <div class="layout-tabs">
    {#each layouts as l}
      <button class:aktiv={aktiv === l.name} onclick={() => (aktiv = l.name)}>
        <i class="fa-solid {l.icon}"></i>
        {l.name}
      </button>
    {/each}
    <button class="still" title="Neues Layout"><i class="fa-solid fa-plus"></i></button>
  </div>
  <div class="kopf-rechts">
    <button class="knopf primaer" onclick={() => (ui.katalog = true)}><i class="fa-solid fa-plus"></i> Kachel</button>
    <button class="icon-knopf" title="Erscheinungsbild" onclick={themaUmschalten}>
      <i class="fa-solid {thema.wert === 'hell' ? 'fa-moon' : 'fa-sun'}"></i>
    </button>
    <button class="icon-knopf" title="Hilfe" onclick={() => (ui.hilfe = true)}><i class="fa-solid fa-circle-question"></i></button>
  </div>
</header>
