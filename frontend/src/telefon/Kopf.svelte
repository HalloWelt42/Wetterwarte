<script lang="ts">
  // Kopf der Übersicht: Ort (Tippen öffnet die Orte), Stand mit Frischepunkt, Punkte der Orte.
  // Waagerecht wischen über dem Kopf wechselt zum nächsten oder vorigen Ort.
  import { orteState } from "../kern/orte.svelte";
  import { uhr } from "../kern/uhr.svelte";
  import { vorZeit } from "../kern/zeit";
  import { ansicht, oeffne, waehleOrt } from "./ansicht.svelte";
  import { nachbarOrt } from "./orte.svelte";
  import { TAKT_MS, standVon } from "./wetter.svelte";
  import { wischen } from "./wischen";

  const ort = $derived(orteState.liste.find((o) => o.slug === ansicht.ort));
  const stand = $derived(standVon(ansicht.ort));
  const alter = $derived(stand.geholt ? uhr.jetzt.getTime() - stand.geholt : Infinity);
  const frische = $derived(stand.zustand === "fehlt" || alter > 60 * 60_000 ? "weg" : stand.zustand === "alt" || alter > 3 * TAKT_MS ? "alt" : "");
  const text = $derived(
    !stand.geholt ? (stand.zustand === "fehlt" ? "keine Verbindung" : "lädt") : frische ? `Stand ${vorZeit(new Date(stand.geholt).toISOString(), uhr.jetzt)}` : vorZeit(new Date(stand.geholt).toISOString(), uhr.jetzt),
  );
</script>

<header class="kopf" use:wischen={{ links: () => waehleOrt(nachbarOrt(ansicht.ort, 1)), rechts: () => waehleOrt(nachbarOrt(ansicht.ort, -1)) }}>
  <div class="kopf-zeile">
    <button class="kopf-ort" onclick={() => oeffne({ art: "orte" })} aria-label="Orte">
      <span class="name">{ort?.name ?? "Wetterwarte"}</span><i class="fa-solid fa-chevron-down"></i>
    </button>
    <span class="kopf-stand {frische}"><span class="frische"></span>{text}</span>
  </div>
  {#if orteState.liste.length > 1}
    <div class="ort-punkte" aria-hidden="true">
      {#each orteState.liste as o (o.slug)}<span class:an={o.slug === ansicht.ort}></span>{/each}
    </div>
  {/if}
</header>
