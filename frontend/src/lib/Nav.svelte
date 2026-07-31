<script lang="ts">
  import { onMount } from "svelte";
  import { route, gehe, type Ansicht } from "./route.svelte";
  import { wetter, ladeWetter } from "./wetter.svelte";
  import { orteState, entferneOrt, startOrt, sortiereOrte, type Ort } from "./orte.svelte";
  import { ui } from "./ui.svelte";
  import { layoutState, setzeAktiv } from "./layout.svelte";
  import { hilfe } from "./hilfeStore.svelte";
  import { hole } from "./api";

  const layoutIcons: Record<string, string> = {
    Zuhause: "fa-house",
    Garten: "fa-seedling",
    Reise: "fa-suitcase-rolling",
    Unwetter: "fa-triangle-exclamation",
  };

  // Mobile Schublade schliessen (auf dem Desktop ohne Wirkung).
  function schliesse(): void {
    ui.menu = false;
  }
  function zeige(ansicht: Ansicht): void {
    gehe(ansicht);
    schliesse();
  }
  function waehleLayout(id: string): void {
    setzeAktiv(id);
    gehe("dashboard");
    schliesse();
  }

  // Orte per Drag-and-Drop umsortieren.
  let ziehIndex = $state<number | null>(null);
  function ablegen(ziel: number): void {
    if (ziehIndex === null || ziehIndex === ziel) {
      ziehIndex = null;
      return;
    }
    const liste = [...orteState.liste];
    const [bewegt] = liste.splice(ziehIndex, 1);
    liste.splice(ziel, 0, bewegt);
    orteState.liste = liste;
    ziehIndex = null;
    void sortiereOrte(liste.map((o) => o.id));
  }

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
    schliesse();
  }

  async function entferne(o: Ort): Promise<void> {
    await entferneOrt(o.id);
    if (wetter.slug === o.slug) {
      const s = startOrt();
      if (s) void ladeWetter(s.slug);
    }
  }
</script>

<!-- Backdrop nur fuer die mobile Schublade; Klick schliesst. -->
<button class="nav-hg nur-mobil" class:offen={ui.menu} aria-label="Menü schließen" onclick={schliesse} tabindex="-1"></button>

<nav class="nav" class:offen={ui.menu}>
  <button class="nav-schliessen nur-mobil" aria-label="Menü schließen" onclick={schliesse}><i class="fa-solid fa-xmark"></i></button>
  <div class="nav-titel">
    Orte
    <button class="plus" title="Demo-Orte (Extremwetter + bekannte Orte)" aria-label="Demo-Orte" onclick={() => (ui.demoOrte = true)}>
      <i class="fa-solid fa-earth-americas"></i>
    </button>
    <button class="plus" title="Ort suchen und hinzufügen" aria-label="Ort suchen und hinzufügen" onclick={() => (ui.ortssuche = true)}>
      <i class="fa-solid fa-plus"></i>
    </button>
  </div>
  {#each orteState.liste as o, i (o.id)}
    <div
      class="nav-ort-wrap"
      class:zieht={ziehIndex === i}
      draggable="true"
      role="listitem"
      ondragstart={() => (ziehIndex = i)}
      ondragover={(e) => e.preventDefault()}
      ondrop={() => ablegen(i)}
      ondragend={() => (ziehIndex = null)}
    >
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
  <button class="nav-eintrag" class:aktiv={route.ansicht === "karte"} onclick={() => zeige("karte")}><i class="fa-solid fa-map-location-dot"></i> <span class="haupt">Große Karte</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "aufzeichnung"} onclick={() => zeige("aufzeichnung")}><i class="fa-solid fa-database"></i> <span class="haupt">Aufzeichnung</span></button>
  <button class="nav-eintrag" class:aktiv={route.ansicht === "archiv"} onclick={() => zeige("archiv")}><i class="fa-solid fa-chart-line"></i> <span class="haupt">Archiv und Analyse</span></button>

  <!-- Layouts und Sekundaer-Aktionen: auf dem Desktop in der Kopfleiste, auf Mobil nur hier erreichbar. -->
  <div class="nav-titel nur-mobil" style="margin-top: var(--a3)">Layouts</div>
  {#each layoutState.liste as l (l.id)}
    <button class="nav-eintrag nur-mobil" class:aktiv={route.ansicht === "dashboard" && layoutState.aktivId === l.id} onclick={() => waehleLayout(l.id)}>
      <i class="fa-solid {layoutIcons[l.name] ?? 'fa-table-cells-large'}"></i> <span class="haupt">{l.name}</span>
    </button>
  {/each}

  <div class="nav-titel nur-mobil" style="margin-top: var(--a3)">Mehr</div>
  <button class="nav-eintrag nur-mobil" onclick={() => { ui.katalog = true; schliesse(); }}><i class="fa-solid fa-plus"></i> <span class="haupt">Kachel hinzufügen</span></button>
  <button class="nav-eintrag nur-mobil" onclick={() => { ui.layouts = true; schliesse(); }}><i class="fa-solid fa-object-group"></i> <span class="haupt">Layouts verwalten</span></button>
  <button class="nav-eintrag nur-mobil" onclick={() => { ui.dienste = true; schliesse(); }}><i class="fa-solid fa-gear"></i> <span class="haupt">System und Dienste</span></button>
  <button class="nav-eintrag nur-mobil" onclick={() => { ui.willkommen = true; schliesse(); }}><i class="fa-solid fa-life-ring"></i> <span class="haupt">Erste Schritte</span></button>
  <button class="nav-eintrag nur-mobil" onclick={() => { hilfe.toggle("uebersicht"); schliesse(); }}><i class="fa-solid fa-circle-question"></i> <span class="haupt">Hilfe</span></button>
  <button class="nav-eintrag nur-mobil" onclick={() => { ui.spende = true; schliesse(); }}><i class="fa-solid fa-heart" style="color: var(--gefahr)"></i> <span class="haupt">Danke sagen</span></button>

  <div class="nav-fuss">
    <div class="nav-quelle"><span class="pulspunkt"></span> DWD + Open-Meteo - aktuell</div>
    <div class="nav-version">{`Wetterwarte${version ? " v" + version : ""} - lokal`}</div>
  </div>
</nav>
