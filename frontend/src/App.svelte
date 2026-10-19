<script lang="ts">
  import { onMount } from "svelte";
  import Kopf from "./lib/Kopf.svelte";
  import Nav from "./lib/Nav.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Karte from "./lib/Karte.svelte";
  import Aufzeichnung from "./lib/Aufzeichnung.svelte";
  import Archiv from "./lib/Archiv.svelte";
  import Katalog from "./lib/Katalog.svelte";
  import Hilfe from "./lib/Hilfe.svelte";
  import Layouts from "./lib/Layouts.svelte";
  import KachelEinstellungen from "./lib/KachelEinstellungen.svelte";
  import Ortssuche from "./lib/Ortssuche.svelte";
  import Dienste from "./lib/Dienste.svelte";
  import DemoOrte from "./lib/DemoOrte.svelte";
  import Spende from "./lib/Spende.svelte";
  import Willkommen from "./lib/Willkommen.svelte";
  import { route, ortAusUrl, profilAusUrl, setzeOrtInUrl, setzeProfilInUrl, initUrl } from "./lib/route.svelte";
  import { ui } from "./lib/ui.svelte";
  import { ladeLayouts, layoutState, setzeAktiv } from "./lib/layout.svelte";
  import { ladeWetter, wetter } from "./lib/wetter.svelte";
  import { ladeOrte, startOrt, orteState } from "./kern/orte.svelte";
  import { stil } from "./lib/stil.svelte";
  import { hilfe } from "./lib/hilfeStore.svelte";
  import { lies, schreib } from "./kern/speicher";
  import { fassung, fassungVerfolgen, neuLadenAufhalten, ruhig } from "./kern/fassung.svelte";

  onMount(() => fassungVerfolgen());
  // Offener Dialog oder laufende Ortssuche: eine neue Fassung wartet bis danach.
  onMount(() =>
    neuLadenAufhalten(
      () => ui.katalog || ui.layouts || ui.ortssuche || ui.einstellungen || ui.dienste || ui.demoOrte || ui.spende || ui.willkommen,
    ),
  );

  onMount(async () => {
    // URL-Parameter ZUERST lesen - bevor asynchrone Ladevorgaenge und die
    // URL-Spiegel-Effekte laufen und die Query normalisieren koennten.
    const profilUrl = profilAusUrl();
    const ausUrl = ortAusUrl();
    await ladeLayouts();
    // Profil-Deep-Link (?profil=<id>) hat Vorrang vor dem Standard-Layout.
    if (profilUrl && layoutState.liste.find((l) => l.id === profilUrl)) setzeAktiv(profilUrl);
    await ladeOrte();
    // Ort-Wahl: Deep-Link aus der URL (?ort=) hat Vorrang, dann der zuletzt
    // betrachtete Ort, sonst der Start-Ort.
    const gemerkt = lies<string>("ort.aktiv", "");
    const s =
      (ausUrl && orteState.liste.find((o) => o.slug === ausUrl)) ||
      (gemerkt && orteState.liste.find((o) => o.slug === gemerkt)) ||
      startOrt();
    if (s) void ladeWetter(s.slug);
    // URL auf den tatsaechlichen Startzustand normalisieren (Ort + aktives Profil).
    initUrl(s?.slug ?? "", layoutState.aktivId ?? "");
    // Beim allerersten Start den Rettungsring einmalig zeigen.
    if (!lies<boolean>("willkommen.gesehen", false)) {
      ui.willkommen = true;
      schreib("willkommen.gesehen", true);
    }
  });

  // Aktiven Ort in der URL spiegeln, sobald er sich aendert (teilbarer Deep-Link).
  $effect(() => {
    if (wetter.slug) setzeOrtInUrl(wetter.slug);
  });

  // Aktives Profil (Layout) in der URL spiegeln.
  $effect(() => {
    if (layoutState.aktivId) setzeProfilInUrl(layoutState.aktivId);
  });

  // Fensterlogik: Oeffnet sich ein zentriertes Modal, tritt das schwebende
  // Hilfe-Fenster zurueck, damit es das Modal nicht verdeckt. Nur auf der
  // steigenden Flanke (Modal geht auf) - aus einem Modal heraus laesst sich die
  // Hilfe per Info-Knopf jederzeit wieder darueber holen.
  let modalWarOffen = false;
  $effect(() => {
    const modalOffen =
      ui.katalog || ui.dienste || ui.spende || ui.willkommen || ui.layouts || ui.demoOrte || ui.einstellungen;
    if (modalOffen && !modalWarOffen && hilfe.open) hilfe.close();
    modalWarOffen = modalOffen;
  });

  function stimmungFuer(icon?: string): string {
    if (!icon) return "tag-klar";
    if (icon.includes("night")) return "nacht-klar";
    if (icon.startsWith("rain") || icon.startsWith("drizzle") || icon.startsWith("thunder")) return "regen";
    if (icon.startsWith("overcast") || icon === "cloudy" || icon.startsWith("fog")) return "tag-wolkig";
    return "tag-klar";
  }
  const appKlasse = $derived(stil.atmo ? `app atmo ${stimmungFuer(wetter.aktuell?.icon)}` : "app");
</script>

<div class={appKlasse}>
  <Kopf />
  <Nav />
  {#if route.ansicht === "karte"}
    <Karte />
  {:else if route.ansicht === "aufzeichnung"}
    <Aufzeichnung />
  {:else if route.ansicht === "archiv"}
    <Archiv />
  {:else}
    <Dashboard />
  {/if}
</div>

{#if fassung.neu}
  <div class="fassung-band" role="status">
    <i class="fa-solid fa-rotate"></i>
    <span>
      <strong>Neue Fassung {fassung.neu} ist da.</strong>
      {ruhig() ? "Beim nächsten Wechsel von Ansicht, Ort oder Profil lädt die Wetterwarte sie von selbst." : "Sie lädt beim nächsten Wechsel von selbst, sobald kein Dialog mehr offen ist und das Radar steht."}
    </span>
    <button class="knopf primaer klein" onclick={() => location.reload()}><i class="fa-solid fa-rotate"></i> Jetzt neu laden</button>
  </div>
{/if}

{#if ui.katalog}<Katalog />{/if}
<Hilfe />
{#if ui.layouts}<Layouts />{/if}
{#if ui.ortssuche}<Ortssuche />{/if}
{#if ui.demoOrte}<DemoOrte />{/if}
{#if ui.einstellungen}<KachelEinstellungen />{/if}
{#if ui.dienste}<Dienste />{/if}
{#if ui.spende}<Spende />{/if}
{#if ui.willkommen}<Willkommen />{/if}
