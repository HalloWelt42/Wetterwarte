<script lang="ts">
  // Kalender-Kachel in mehreren Varianten (Monat, Tag). Kein Ortsbezug.
  import { uhr } from "../../uhr.svelte";

  let { conf = {} }: { conf?: Record<string, any>; ort?: string } = $props();
  const variante = $derived((conf.variante as string) ?? "monat");

  const jahr = $derived(uhr.jetzt.getFullYear());
  const monat = $derived(uhr.jetzt.getMonth());
  const heute = $derived(uhr.jetzt.getDate());
  const monatsName = $derived(uhr.jetzt.toLocaleDateString("de-DE", { month: "long", year: "numeric" }));
  const tagName = $derived(uhr.jetzt.toLocaleDateString("de-DE", { weekday: "long" }));

  const wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
  const zellen = $derived.by(() => {
    const erster = new Date(jahr, monat, 1);
    const start = (erster.getDay() + 6) % 7; // Montag = 0
    const anzahl = new Date(jahr, monat + 1, 0).getDate();
    const out: (number | null)[] = [];
    for (let i = 0; i < start; i++) out.push(null);
    for (let d = 1; d <= anzahl; d++) out.push(d);
    return out;
  });
</script>

{#if variante === "tag"}
  <div class="kal-tag">
    <div class="kal-tag-wtag">{tagName}</div>
    <div class="kal-tag-zahl tnum">{heute}</div>
    <div class="kal-tag-monat dimm">{monatsName}</div>
  </div>
{:else}
  <div class="kal-kopf">{monatsName}</div>
  <div class="kal-grid">
    {#each wochentage as w}<span class="kal-wt">{w}</span>{/each}
    {#each zellen as d}<span class="kal-zelle" class:heute={d === heute}>{d ?? ""}</span>{/each}
  </div>
{/if}
