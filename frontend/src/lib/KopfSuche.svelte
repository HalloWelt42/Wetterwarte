<script lang="ts">
  // Inline-Ortssuche im Kopf: tippen zeigt direkt eine Trefferliste (Geokodierung).
  // Ein Treffer, der schon in der Liste ist, wird nur aktiviert; ein neuer wird
  // hinzugefuegt. Ersetzt das alte, nur-lesbare Suchfeld, das bloss ein Modal oeffnete.
  import { sucheOrte, fuegeOrtHinzu, orteState, type Treffer } from "./orte.svelte";
  import { ladeWetter } from "./wetter.svelte";
  import { gehe } from "./route.svelte";

  let begriff = $state("");
  let treffer = $state<Treffer[]>([]);
  let laedt = $state(false);
  let offen = $state(false);
  let entprellen: ReturnType<typeof setTimeout> | undefined;

  function eingabe(): void {
    clearTimeout(entprellen);
    const q = begriff;
    offen = true;
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

  function vorhandenerOrt(t: Treffer) {
    return orteState.liste.find((o) => Math.abs(o.lat - t.lat) < 0.02 && Math.abs(o.lon - t.lon) < 0.02);
  }

  async function waehle(t: Treffer): Promise<void> {
    const da = vorhandenerOrt(t);
    let slug = da?.slug;
    if (!slug) {
      const neu = await fuegeOrtHinzu(t);
      slug = neu?.slug;
    }
    schliesse();
    if (slug) {
      void ladeWetter(slug);
      gehe("dashboard");
    }
  }

  function schliesse(): void {
    offen = false;
    begriff = "";
    treffer = [];
  }

  function taste(e: KeyboardEvent): void {
    if (e.key === "Escape") schliesse();
  }
</script>

<div class="kopf-suche-wrap">
  <div class="kopf-suche">
    <i class="fa-solid fa-magnifying-glass"></i>
    <input
      type="text"
      placeholder="Ort suchen ..."
      bind:value={begriff}
      oninput={eingabe}
      onfocus={() => (offen = true)}
      onkeydown={taste}
    />
  </div>

  {#if offen && begriff.trim().length >= 1}
    <!-- Klick ausserhalb schliesst die Liste. -->
    <div class="kopf-suche-hg" role="presentation" onclick={schliesse}></div>
    <div class="kopf-suche-liste">
    {#if laedt}
      <div class="such-hinweis">Suche läuft ...</div>
    {:else if begriff.trim().length < 2}
      <div class="such-hinweis">Mindestens zwei Zeichen. Weltweite Suche.</div>
    {:else if treffer.length === 0}
      <div class="such-hinweis">Kein Ort gefunden.</div>
    {:else}
      {#each treffer as t}
        <button class="kat-item" style="width: 100%; text-align: left; font: inherit" onclick={() => waehle(t)}>
          <i class="fa-solid fa-location-dot"></i>
          <span class="kat-txt">{t.name}<small>{[t.region, t.land].filter(Boolean).join(" · ")}</small></span>
          {#if vorhandenerOrt(t)}<small class="dimm">anzeigen</small>{:else}<i class="fa-solid fa-plus griff"></i>{/if}
        </button>
      {/each}
    {/if}
    </div>
  {/if}
</div>
