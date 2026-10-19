<script lang="ts">
  // Untertitel der laufenden Ansage über der Reiterleiste: was gesprochen wird, steht auch da (ohne Ton lesbar).
  // Tippen beendet die Ansage.
  import { ansagen, verstummen } from "./ansagen.svelte";
</script>

{#if ansagen.spricht}
  {@const a = ansagen.spricht}
  <button class="untertitel stufe-{Math.min(4, Math.max(1, a.stufe))}" class:entwarnung={a.entwarnung} onclick={verstummen} aria-live="polite">
    <span class="stufe-marke"><i class="fa-solid fa-volume-high"></i></span>
    <span class="ut-text"><b>{a.titel}</b><span>{a.text}</span></span>
    <span class="ut-stopp" aria-label="Ansage beenden"><i class="fa-solid fa-stop"></i></span>
  </button>
{/if}

<style>
  .untertitel {
    position: fixed;
    left: var(--rand);
    right: var(--rand);
    bottom: calc(var(--leiste-h) + var(--sicher-unten) + 8px);
    z-index: 30;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: var(--radius);
    text-align: left;
    box-shadow: 0 6px 24px rgb(0 0 0 / 0.35);
  }
  .untertitel.entwarnung {
    background: var(--flaeche-2);
  }
  .entwarnung .stufe-marke {
    background: var(--flaeche-3);
    color: var(--gut);
  }
  .ut-text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
    line-height: 1.3;
  }
  .ut-text b {
    font-size: var(--s17);
  }
  .ut-text span {
    font-size: var(--s15);
    color: var(--text-2);
  }
  .ut-stopp {
    color: var(--text-3);
    font-size: var(--s17);
  }
</style>
