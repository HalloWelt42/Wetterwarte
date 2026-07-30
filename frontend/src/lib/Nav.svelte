<script lang="ts">
  import { onMount } from "svelte";
  import { route, gehe } from "./route.svelte";
  import { wetter, ladeWetter } from "./wetter.svelte";
  import { orteState, entferneOrt, startOrt, type Ort } from "./orte.svelte";
  import { ui } from "./ui.svelte";
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

  function waehle(o: Ort): void {
    void ladeWetter(o.slug);
    gehe("dashboard");
  }

  async function entferne(o: Ort): Promise<void> {
    await entferneOrt(o.id);
    if (wetter.slug === o.slug) {
      const s = startOrt();
      if (s) void ladeWetter(s.slug);
    }
  }
</script>

<nav class="nav">
  <div class="nav-titel">
    Orte
    <button class="plus" title="Ort suchen und hinzufügen" aria-label="Ort suchen und hinzufügen" onclick={() => (ui.ortssuche = true)}>
      <i class="fa-solid fa-plus"></i>
    </button>
  </div>
  {#each orteState.liste as o (o.id)}
    <div class="nav-ort-wrap">
      <button class="nav-eintrag" class:aktiv={route.ansicht === "dashboard" && wetter.slug === o.slug} onclick={() => waehle(o)}>
        <i class="fa-solid fa-location-dot ort-punkt"></i>
        <span class="haupt">{o.name} <small>{o.region}</small></span>
      </button>
      <button class="ort-weg" title="Ort entfernen" aria-label="Ort entfernen" onclick={() => entferne(o)}>
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  {/each}
  {#if orteState.liste.length === 0}
    <button class="nav-eintrag" onclick={() => (ui.ortssuche = true)}>
      <i class="fa-solid fa-magnifying-glass ort-punkt"></i>
      <span class="haupt">Ort suchen <small>noch keine Orte</small></span>
    </button>
  {/if}

  <div class="nav-titel" style="margin-top: var(--a3)">Ansichten</div>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "karte"} onclick={() => gehe("karte")}><i class="fa-solid fa-map-location-dot"></i> <span class="haupt">Große Karte</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "aufzeichnung"} onclick={() => gehe("aufzeichnung")}><i class="fa-solid fa-database"></i> <span class="haupt">Aufzeichnung</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "archiv"} onclick={() => gehe("archiv")}><i class="fa-solid fa-chart-line"></i> <span class="haupt">Archiv und Analyse</span></button>

  <div class="nav-fuss">
    <div class="nav-quelle"><span class="pulspunkt"></span> DWD + Open-Meteo - aktuell</div>
    <div class="nav-version">{`Wetterwarte${version ? " v" + version : ""} - lokal`}</div>
  </div>
</nav>
