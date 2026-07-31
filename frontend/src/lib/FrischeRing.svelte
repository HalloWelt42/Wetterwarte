<script lang="ts">
  // Ring-Prozessbalken der Datenfrische: laeuft wie eine Sanduhr ab - beim
  // Auffrischen voll, leert sich bis zur naechsten Basis-Auffrischung (~10 min).
  import { uhr } from "./uhr.svelte";
  import { wetter } from "./wetter.svelte";

  const INTERVALL = 600_000; // 10-min-Basis-Takt (siehe wetter.svelte.ts)
  const verstrichen = $derived(wetter.aktualisiert ? uhr.jetzt.getTime() - wetter.aktualisiert : INTERVALL);
  const anteil = $derived(Math.min(1, Math.max(0, verstrichen / INTERVALL)));

  const R = 8;
  const UMFANG = 2 * Math.PI * R;

  const minuten = $derived(Math.floor(verstrichen / 60000));
  const text = $derived(!wetter.aktualisiert ? "lädt ..." : minuten < 1 ? "aktualisiert soeben" : `aktualisiert vor ${minuten} Min`);
  const restMin = $derived(Math.max(0, Math.ceil((INTERVALL - verstrichen) / 60000)));
</script>

<span class="frische" title="Nächste Auffrischung in etwa {restMin} Min">
  <svg viewBox="0 0 20 20" class="frische-ring" aria-hidden="true">
    <circle cx="10" cy="10" r="8" fill="none" stroke="var(--rand)" stroke-width="2.4" />
    <circle
      cx="10"
      cy="10"
      r="8"
      fill="none"
      stroke="var(--akzent)"
      stroke-width="2.4"
      stroke-linecap="round"
      stroke-dasharray={UMFANG}
      stroke-dashoffset={UMFANG * anteil}
      transform="rotate(-90 10 10)"
    />
  </svg>
  <small>{text}</small>
</span>
