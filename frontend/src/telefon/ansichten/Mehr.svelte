<script lang="ts">
  import { profilSymbol } from "../../kern/profilsymbol";
  // Reiter Mehr (Entwurf mockups/telefon/mehr.html): Profil wählen, Schriftstufe und Nachtbetrieb für
  // dieses Gerät, alle Kachelformen, Wechsel zur Desktop-Ansicht, Fassung und Datenquellen.
  // Nur, was am Telefon wirklich gewählt werden kann; eingerichtet wird am Rechner.
  import { orteState } from "../../kern/orte.svelte";
  import { OBERFLAECHE_FASSUNG } from "../../kern/fassung.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { uhr } from "../../kern/uhr.svelte";
  import { ansicht, oeffne } from "../ansicht.svelte";
  import { geraet, setzeNacht, setzeStufe, zurDesktopAnsicht, type Nachtwahl, type Stufe } from "../geraet.svelte";
  import { profile, waehleProfil } from "../profil.svelte";
  import { standVon } from "../wetter.svelte";

  const STUFEN: { wert: Stufe; titel: string }[] = [
    { wert: "normal", titel: "Normal" },
    { wert: "gross", titel: "Groß" },
    { wert: "sehr-gross", titel: "Sehr groß" },
  ];
  const NACHT: { wert: Nachtwahl; titel: string }[] = [
    { wert: "aus", titel: "Aus" },
    { wert: "auto", titel: "Nach Sonnenuntergang" },
    { wert: "an", titel: "An" },
  ];

  // Sonnenauf- und -untergang am gewählten Ort, nach denen sich "Nach Sonnenuntergang" richtet
  const ort = $derived(orteState.liste.find((o) => o.slug === ansicht.ort));
  const daten = $derived(standVon(ansicht.ort).daten);
  const zone = $derived(daten?.ort.zeitzone ?? ort?.zeitzone ?? "");
  const sonne = $derived.by(() => {
    const t = daten?.tage[0];
    if (!t?.sonnenaufgang || !t.sonnenuntergang) return "";
    return `, in ${ort?.name ?? daten!.ort.name} heute ${uhrzeit(t.sonnenaufgang, zone)} und ${uhrzeit(t.sonnenuntergang, zone)} Uhr`;
  });
</script>

<div class="rollfeld">
  <header class="kopf">
    <div class="kopf-zeile"><h1 class="seiten-titel">Mehr</h1></div>
  </header>
  <main class="mehr-liste">
    <section class="abschnitt">
      <h3>Profil</h3>
      {#if profile.liste.length}
        <div class="zeilen">
          {#each profile.liste as p (p.id)}
            {@const aktiv = p.id === profile.aktivId}
            <button class="zeile" class:an={aktiv} aria-current={aktiv ? "true" : undefined} onclick={() => waehleProfil(p.id)}>
              <span class="sym"><i class="fa-solid {profilSymbol(p)}"></i></span>
              <span class="haupt"><b>{p.name}</b>{#if p.ist_standard}<small>Startprofil</small>{/if}</span>
              {#if aktiv}<span class="rechts"><i class="fa-solid fa-check"></i></span>{/if}
            </button>
          {/each}
        </div>
      {:else}
        <p class="hinweis-z"><i class="fa-solid fa-plug-circle-xmark"></i><span>{profile.geladen ? "Keine Profile erreichbar." : "Profile werden geladen ..."}</span></p>
      {/if}
      <p class="hinweis-z"><i class="fa-solid fa-desktop"></i><span>Das Telefon-Layout wird am Rechner in der Layout-Verwaltung eingerichtet.</span></p>
    </section>

    <section class="abschnitt">
      <h3>Anzeige</h3>
      <div class="einstellung">
        <div class="einst-kopf"><b>Schriftstufe</b><small>nur dieses Gerät</small></div>
        <div class="segmente" role="radiogroup" aria-label="Schriftstufe">
          {#each STUFEN as s (s.wert)}
            <button class:an={geraet.stufe === s.wert} role="radio" aria-checked={geraet.stufe === s.wert} onclick={() => setzeStufe(s.wert)}>{s.titel}</button>
          {/each}
        </div>
      </div>
      <div class="einstellung">
        <div class="einst-kopf"><b>Nachtbetrieb</b><small>nur Rot, gedämpft</small></div>
        <div class="segmente nach-inhalt" role="radiogroup" aria-label="Nachtbetrieb">
          {#each NACHT as n (n.wert)}
            <button class:an={geraet.nacht === n.wert} role="radio" aria-checked={geraet.nacht === n.wert} onclick={() => setzeNacht(n.wert)}>{n.titel}</button>
          {/each}
        </div>
        {#if geraet.nacht === "auto"}<div class="einst-unter">Richtet sich nach Sonnenauf- und -untergang am gewählten Ort{sonne}.</div>{/if}
        {#if geraet.nacht === "auto" && geraet.uebersteuerung && geraet.uebersteuerung.bis > uhr.jetzt.getTime()}
          <div class="einst-unter">
            Von Hand {geraet.uebersteuerung.nacht ? "eingeschaltet" : "ausgeschaltet"} bis {uhrzeit(new Date(geraet.uebersteuerung.bis), zone)} Uhr, danach wieder nach der Sonne.
          </div>
        {/if}
      </div>
    </section>

    <section class="abschnitt">
      <h3>Ansicht</h3>
      <div class="zeilen">
        <button class="zeile" onclick={() => oeffne({ art: "schaukasten" })}>
          <span class="sym"><i class="fa-solid fa-table-cells"></i></span>
          <span class="haupt"><b>Alle Kachelformen</b><small>Jede Kachel in jeder Größe mit den Daten des Orts</small></span>
          <span class="rechts"><i class="fa-solid fa-chevron-right"></i></span>
        </button>
        <button class="zeile" onclick={zurDesktopAnsicht}>
          <span class="sym"><i class="fa-solid fa-desktop"></i></span>
          <span class="haupt"><b>Zur Desktop-Ansicht</b><small>Dieses Gerät merkt sich die Wahl</small></span>
          <span class="rechts"><i class="fa-solid fa-arrow-right"></i></span>
        </button>
      </div>
    </section>

    <section class="abschnitt">
      <h3>Über</h3>
      <div class="zeilen">
        <div class="zeile">
          <span class="sym"><i class="fa-solid fa-code-branch"></i></span>
          <span class="haupt"><b>Fassung</b><small>lädt nach dem Ausrollen von selbst neu</small></span>
          <span class="rechts zahl">{OBERFLAECHE_FASSUNG}</span>
        </div>
        <div class="zeile">
          <span class="sym"><i class="fa-solid fa-database"></i></span>
          <span class="haupt"><b>Datenquellen</b><small>Deutscher Wetterdienst, außerhalb Deutschlands offene Wettermodelle. Karte: OpenStreetMap-Mitwirkende.</small></span>
        </div>
      </div>
    </section>
  </main>
</div>

<style>
  .seiten-titel {
    margin: 0;
    padding-left: 6px;
    font-size: var(--s26);
    font-weight: 700;
    line-height: 1.1;
  }
  .mehr-liste {
    padding: 0 var(--rand);
  }
  :global(.tel) .mehr-liste button.zeile {
    width: 100%;
    padding: 6px 14px;
    text-align: left;
  }
  :global(.tel) .mehr-liste .zeile .haupt small {
    white-space: normal;
    line-height: 1.25;
  }
  .rechts .fa-check {
    color: var(--akzent);
    font-size: var(--s19);
  }
  .rechts .fa-arrow-right {
    color: var(--text-3);
    font-size: var(--s15);
  }
  .hinweis-z {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 10px 8px 0;
    font-size: var(--s15);
    color: var(--text-3);
    line-height: 1.35;
  }
  .hinweis-z i {
    margin-top: 3px;
  }
  .einstellung + .einstellung {
    margin-top: 18px;
  }
  .einst-kopf {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 4px 10px;
    margin: 0 8px 8px;
  }
  .einst-kopf b {
    font-weight: 700;
  }
  .einst-kopf small {
    font-size: var(--s15);
    color: var(--text-3);
  }
  :global(.tel) .segmente.nach-inhalt button {
    flex: 1 1 auto;
    padding: 4px 12px;
    line-height: 1.15;
  }
  .einst-unter {
    margin: 8px 8px 0;
    font-size: var(--s15);
    color: var(--text-2);
    line-height: 1.35;
  }
</style>
