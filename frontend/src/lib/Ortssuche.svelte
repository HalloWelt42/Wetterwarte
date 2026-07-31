<script lang="ts">
  import { ui } from "./ui.svelte";
  import { sucheOrte, fuegeOrtHinzu, orteState, type Treffer } from "./orte.svelte";
  import { ladeWetter } from "./wetter.svelte";
  import { gehe } from "./route.svelte";

  let begriff = $state("");
  let treffer = $state<Treffer[]>([]);
  let laedt = $state(false);
  let entprellen: ReturnType<typeof setTimeout> | undefined;

  function eingabe(): void {
    clearTimeout(entprellen);
    const q = begriff;
    if (q.trim().length < 2) {
      treffer = [];
      laedt = false;
      return;
    }
    laedt = true;
    entprellen = setTimeout(async () => {
      treffer = await sucheOrte(q);
      laedt = false;
    }, 300);
  }

  function schonVorhanden(t: Treffer): boolean {
    return orteState.liste.some((o) => Math.abs(o.lat - t.lat) < 0.02 && Math.abs(o.lon - t.lon) < 0.02);
  }

  async function waehle(t: Treffer): Promise<void> {
    const neu = await fuegeOrtHinzu(t);
    ui.ortssuche = false;
    if (neu) {
      void ladeWetter(neu.slug);
      gehe("dashboard");
    }
  }

  function zu(): void {
    ui.ortssuche = false;
  }
</script>

<div class="ueberlagerung" role="presentation" onclick={zu}></div>
<aside class="seiten-panel">
  <div class="detail-kopf">
    <h2><i class="fa-solid fa-location-dot"></i> Ort suchen</h2>
    <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
  </div>
  <div class="detail-block">
    <div class="feld-such">
      <i class="fa-solid fa-magnifying-glass"></i>
      <!-- svelte-ignore a11y_autofocus -->
      <input type="text" placeholder="Stadt oder Ort eingeben ..." bind:value={begriff} oninput={eingabe} autofocus />
    </div>
  </div>
  <div style="flex: 1; overflow-y: auto; padding: 0 var(--a4) var(--a4)">
    {#if laedt}
      <div class="such-hinweis">Suche läuft ...</div>
    {:else if begriff.trim().length < 2}
      <div class="such-hinweis">Mindestens zwei Zeichen eingeben. Weltweite Suche.</div>
    {:else if treffer.length === 0}
      <div class="such-hinweis">Kein Ort gefunden.</div>
    {:else}
      {#each treffer as t}
        <button
          class="kat-item"
          style="width: 100%; text-align: left; font: inherit"
          onclick={() => waehle(t)}
          disabled={schonVorhanden(t)}
        >
          <i class="fa-solid fa-location-dot"></i>
          <span class="kat-txt">{t.name}<small>{[t.region, t.land].filter(Boolean).join(" · ")}</small></span>
          {#if schonVorhanden(t)}
            <small class="dimm">bereits da</small>
          {:else}
            <i class="fa-solid fa-plus griff"></i>
          {/if}
        </button>
      {/each}
    {/if}
  </div>
</aside>
