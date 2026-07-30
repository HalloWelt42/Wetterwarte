<script lang="ts">
  import { nutzeOrtDaten } from "../../ortdaten.svelte";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  const allergien = $derived((conf.allergien as string[]) ?? []);

  // Pollen (DWD-Gefahrenindex): Tag-Auswahl + nach Belastung sortiert.
  const pollenDaten = $derived(daten.pollen);
  let pollenTag = $state<"today" | "tomorrow" | "dayafter">("today");
  const pollenTage = [
    { key: "today", label: "Heute" },
    { key: "tomorrow", label: "Morgen" },
    { key: "dayafter", label: "Übermorgen" },
  ] as const;
  const pollenSortiert = $derived.by(() => {
    if (!pollenDaten) return [];
    return Object.values(pollenDaten.arten)
      .map((a) => ({ icon: a.icon, name: a.name, stufe: a[pollenTag], allergie: allergien.includes(a.name) }))
      .sort((x, y) => {
        if (x.allergie !== y.allergie) return x.allergie ? -1 : 1;
        return y.stufe.value - x.stufe.value;
      });
  });
  function pollenBreite(v: number): number {
    return v < 0 ? 0 : Math.min((v / 3) * 100, 100);
  }
</script>

{#if pollenDaten}
  <div class="pollen-kopf">
    <span class="pollen-region">{pollenDaten.region.name}{#if pollenDaten.region.partregion_name}&nbsp;<span class="dimm">&middot; {pollenDaten.region.partregion_name}</span>{/if}</span>
  </div>
  <div class="pollen-tabs">
    {#each pollenTage as t}
      <button class="pollen-tab" class:aktiv={pollenTag === t.key} onclick={() => (pollenTag = t.key)}>{t.label}</button>
    {/each}
  </div>
  <div class="pollen-liste">
    {#each pollenSortiert as p}
      <div class="pollen-zeile" class:allergie={p.allergie} class:hat-last={p.stufe.value > 0} class:viel-last={p.stufe.value >= 2}>
        <span class="pollen-info"><span class="pollen-emoji">{p.icon}</span><span class="pollen-name">{p.name}</span>{#if p.allergie}<span class="allergie-punkt" title="Deine Allergie">🔴</span>{/if}</span>
        <span class="pollen-pegel">
          <span class="pegel-bahn"><span class="pegel-fuell" style="width: {pollenBreite(p.stufe.value)}%; background: {p.stufe.color}"></span></span>
          <span class="pegel-label" style="color: {p.stufe.color}">{p.stufe.label}</span>
        </span>
      </div>
    {/each}
  </div>
  <div class="pollen-stand">Stand: {pollenDaten.last_update}</div>
{:else}
  <div class="kw-leer"><i class="fa-solid fa-seedling"></i><div>Keine Pollendaten</div></div>
{/if}
