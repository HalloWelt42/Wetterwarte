<script lang="ts">
  import { onMount } from "svelte";
  import { meteocon } from "./icons";
  import { orte } from "./platzhalter";
  import { route, gehe } from "./route.svelte";
  import { wetter, ladeWetter } from "./wetter.svelte";
  import { hole } from "./api";

  let version = $state("");
  onMount(async () => {
    try {
      const h = await hole<{ status: string; version: string }>("/health");
      version = h.version;
    } catch {
      // Ohne Backend bleibt die Version leer.
    }
  });
</script>

<nav class="nav">
  <div class="nav-titel">
    Orte
    <button class="plus" title="Ort hinzufügen"><i class="fa-solid fa-plus"></i></button>
  </div>
  {#each orte as o}
    <button
      class="nav-eintrag"
      class:aktiv={route.ansicht === "dashboard" && wetter.slug === o.slug}
      onclick={() => {
        void ladeWetter(o.slug);
        gehe("dashboard");
      }}
    >
      <img class="mc winzig" src={meteocon(o.icon)} alt="" />
      <span class="haupt">{o.name} <small>{o.region}</small></span>
      <span class="grad">{o.temp}&deg;</span>
    </button>
  {/each}

  <div class="nav-titel" style="margin-top: var(--a3)">Ansichten</div>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "karte"} onclick={() => gehe("karte")}><i class="fa-solid fa-map-location-dot"></i> <span class="haupt">Große Karte</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "aufzeichnung"} onclick={() => gehe("aufzeichnung")}><i class="fa-solid fa-database"></i> <span class="haupt">Aufzeichnung</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "archiv"} onclick={() => gehe("archiv")}><i class="fa-solid fa-chart-line"></i> <span class="haupt">Archiv und Analyse</span></button>

  <div class="nav-fuss">
    <div class="nav-quelle"><span class="pulspunkt"></span> DWD + Open-Meteo - aktuell</div>
    <div class="nav-version">{`Wetterwarte${version ? " v" + version : ""} - lokal`}</div>
  </div>
</nav>
