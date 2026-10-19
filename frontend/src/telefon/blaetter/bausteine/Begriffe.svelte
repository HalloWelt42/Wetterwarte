<script lang="ts">
  // Abschnitt mit Fachbegriffen: je Begriff eine Zeile mit (i); Antippen blendet den Erklärtext
  // ein und wieder aus (natives details, nichts hängt am Überfahren).
  import type { Begriff } from "../erklaerungen";

  let { liste, titel = "Begriffe" }: { liste: Begriff[]; titel?: string } = $props();
</script>

{#if liste.length}
  <div class="abschnitt">
    <h3>{titel}</h3>
    <div class="zeilen">
      {#each liste as b (b.titel)}
        <details class="auf erkl">
          <summary><i class="fa-solid fa-circle-info"></i><span>{b.titel}</span><i class="fa-solid fa-chevron-down"></i></summary>
          <p>{b.text}</p>
        </details>
      {/each}
    </div>
  </div>
{/if}
