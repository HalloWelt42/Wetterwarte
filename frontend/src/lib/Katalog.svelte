<script lang="ts">
  import { ui } from "./ui.svelte";
  import { registry, familien } from "./kacheln/registry";
  import { kachelAktion } from "./kachelAktion.svelte";

  const gruppen = familien.map((f) => ({
    name: f,
    eintraege: Object.values(registry).filter((r) => r.familie === f),
  }));

  function zu(): void {
    ui.katalog = false;
  }
  function hinzufuegen(typ: string): void {
    kachelAktion.add = typ;
    ui.katalog = false;
  }
</script>

<div class="ueberlagerung" role="presentation" onclick={zu}></div>
<aside class="seiten-panel">
  <div class="detail-kopf">
    <h2><i class="fa-solid fa-shapes"></i> Kachel hinzufügen</h2>
    <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
  </div>
  <div class="detail-block">
    <div class="feld-such">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" placeholder="Kacheltyp suchen ..." />
    </div>
  </div>
  <div style="flex: 1; overflow-y: auto; padding: 0 var(--a4) var(--a4)">
    {#each gruppen as g}
      <div class="kat-gruppe">{g.name}</div>
      {#each g.eintraege as e}
        <button class="kat-item" style="width: 100%; text-align: left; font: inherit" onclick={() => hinzufuegen(e.typ)}>
          <i class="fa-solid {e.icon}"></i>
          <span class="kat-txt">{e.titel}<small>Kachel hinzufügen</small></span>
          <i class="fa-solid fa-plus griff"></i>
        </button>
      {/each}
    {/each}
  </div>
</aside>
