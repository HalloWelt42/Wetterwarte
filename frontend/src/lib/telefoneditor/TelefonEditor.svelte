<script lang="ts">
  // Telefon-Editor am Desktop (docs/TELEFON.md, Entwurf mockups/telefon-editor.html): links der
  // Telefon-Katalog, in der Mitte ein Telefonrahmen mit den ECHTEN Telefon-Kacheln und den Daten
  // des Vorschau-Orts, rechts die gewählte Kachel (Größe, Einstellungen, Entfernen). Ziehen auf
  // ein Feld verschiebt, die übrigen Kacheln rücken nach. Jede Änderung wird sofort gespeichert.
  import { setContext } from "svelte";
  import "../../telefon/telefon.css";
  import { telefonKatalog, type Einstellung } from "../../kern/gemeinsam";
  import { orteState } from "../../kern/orte.svelte";
  import Kachel from "../../telefon/Kachel.svelte";
  import { ladeWennAlt, standVon } from "../../telefon/wetter.svelte";
  import { layoutState, profilIcon } from "../layout.svelte";
  import { wetter } from "../wetter.svelte";
  import {
    bewege,
    editor,
    entferne,
    gewaehlteKachel,
    hinzufuegen,
    kacheln,
    profil,
    setzeEinstellung,
    setzeGroesse,
    vorlageWiederherstellen,
  } from "./editor.svelte";
  import { reihenVon, SPALTEN } from "./raster";

  setContext("telefon-nacht", () => editor.nacht);

  let vorschauOrt = $state("");
  const ort = $derived(vorschauOrt || wetter.slug || orteState.liste[0]?.slug || "");
  $effect(() => {
    if (ort) ladeWennAlt(ort);
  });
  const stand = $derived(standVon(ort));

  let suche = $state("");
  let entfernenScharf = $state(false);
  let vorlageScharf = $state(false);

  const liste = $derived(kacheln());
  const gewaehlt = $derived(gewaehlteKachel());
  const gDef = $derived(gewaehlt ? telefonKatalog.typen[gewaehlt.typ] : undefined);
  const familien = $derived(
    telefonKatalog.familien
      .map((f) => ({
        ...f,
        typen: Object.entries(telefonKatalog.typen).filter(
          ([typ, d]) =>
            d.familie === f.schluessel &&
            d.seiten.includes(editor.seite) &&
            (!suche || `${d.titel} ${d.beschreibung} ${typ}`.toLowerCase().includes(suche.toLowerCase())),
        ),
      }))
      .filter((f) => f.typen.length),
  );
  const reihen = $derived(reihenVon(liste) + 1); // eine freie Reihe zum Hineinziehen
  const anzahlJeTyp = $derived(liste.reduce<Record<string, number>>((m, k) => ({ ...m, [k.typ]: (m[k.typ] ?? 0) + 1 }), {}));

  // ---- Ziehen im Raster
  let rasterEl = $state<HTMLElement>();
  let zug = $state<{ id: string; dx: number; dy: number; x: number; y: number; w: number; h: number; bewegt: boolean } | null>(null);
  let start: { px: number; py: number; gx: number; gy: number } | null = null;

  function feldmass(): number {
    const f = rasterEl ? parseFloat(getComputedStyle(rasterEl).getPropertyValue("--feld")) : 0;
    return f || 122;
  }
  const FUGE = 6;

  function unten(e: PointerEvent, id: string): void {
    const k = liste.find((x) => x.id === id);
    if (!k || !rasterEl) return;
    const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const schritt = feldmass() + FUGE;
    start = { px: e.clientX, py: e.clientY, gx: Math.floor((e.clientX - r.left) / schritt), gy: Math.floor((e.clientY - r.top) / schritt) };
    zug = { id, dx: 0, dy: 0, x: k.x, y: k.y, w: k.w, h: k.h, bewegt: false };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }
  function bewegt(e: PointerEvent): void {
    if (!zug || !start || !rasterEl) return;
    const dx = e.clientX - start.px;
    const dy = e.clientY - start.py;
    const r = rasterEl.getBoundingClientRect();
    const schritt = feldmass() + FUGE;
    const x = Math.min(Math.max(0, Math.floor((e.clientX - r.left) / schritt) - start.gx), SPALTEN - zug.w);
    const y = Math.max(0, Math.floor((e.clientY - r.top) / schritt) - start.gy);
    zug = { ...zug, dx, dy, x, y, bewegt: zug.bewegt || Math.hypot(dx, dy) > 6 };
  }
  function los(): void {
    if (!zug) return;
    const z = zug;
    zug = null;
    start = null;
    editor.gewaehlt = z.id;
    entfernenScharf = false;
    const k = liste.find((x) => x.id === z.id);
    if (z.bewegt && k && (k.x !== z.x || k.y !== z.y)) bewege(z.id, z.x, z.y);
  }

  // ---- Größe
  const ALLE_GROESSEN = [1, 2, 3].flatMap((h) => [1, 2, 3].map((w) => ({ w, h, g: `${w}x${h}` })));

  function einstellungWert(e: Einstellung): unknown {
    return gewaehlt?.conf[e.schluessel] ?? e.standard;
  }
  function umschalten(e: Einstellung, wert: string): void {
    if (!gewaehlt) return;
    const jetzt = (einstellungWert(e) as string[]) ?? [];
    setzeEinstellung(gewaehlt.id, e.schluessel, jetzt.includes(wert) ? jetzt.filter((x) => x !== wert) : [...jetzt, wert]);
  }

  function entfernen(): void {
    if (!gewaehlt) return;
    if (!entfernenScharf) {
      entfernenScharf = true; // erster Klick schärft, zweiter entfernt
      return;
    }
    entfernenScharf = false;
    entferne(gewaehlt.id);
  }
  function vorlage(): void {
    if (!vorlageScharf) {
      vorlageScharf = true;
      return;
    }
    vorlageScharf = false;
    void vorlageWiederherstellen();
  }
</script>

<section class="inhalt">
  <div class="te">
    <header class="te-kopf">
      <h1><i class="fa-solid fa-mobile-screen"></i> Telefon-Layout</h1>
      <div class="te-profile" role="tablist" aria-label="Profil">
        {#each layoutState.liste as l (l.id)}
          <button role="tab" class:an={profil()?.id === l.id} aria-selected={profil()?.id === l.id} onclick={() => ((editor.profilId = l.id), (editor.gewaehlt = null))}>
            <i class="fa-solid {profilIcon(l)}"></i>{l.name}
          </button>
        {/each}
      </div>
    </header>

    <div class="te-leiste">
      <div class="te-seg" role="tablist" aria-label="Seite">
        {#each telefonKatalog.seiten as s (s.schluessel)}
          <button class:an={editor.seite === s.schluessel} onclick={() => ((editor.seite = s.schluessel), (editor.gewaehlt = null))}><i class="fa-solid {s.symbol}"></i>{s.titel}</button>
        {/each}
      </div>
      <label class="te-feld">
        <span>Vorschau</span>
        <select name="vorschau-ort" value={ort} onchange={(e) => (vorschauOrt = e.currentTarget.value)}>
          {#each orteState.liste as o (o.slug)}<option value={o.slug}>{o.name}</option>{/each}
        </select>
      </label>
      <div class="te-seg" aria-label="Breite">
        {#each [375, 390, 430] as b}<button class:an={editor.breite === b} onclick={() => (editor.breite = b)}>{b}</button>{/each}
      </div>
      <div class="te-seg" aria-label="Tag oder Nacht">
        <button class:an={!editor.nacht} onclick={() => (editor.nacht = false)}><i class="fa-solid fa-sun"></i>Tag</button>
        <button class:an={editor.nacht} onclick={() => (editor.nacht = true)}><i class="fa-solid fa-moon"></i>Nacht</button>
      </div>
      <button class="te-knopf" class:scharf={vorlageScharf} onclick={vorlage} onblur={() => (vorlageScharf = false)}>
        <i class="fa-solid fa-rotate-left"></i>{vorlageScharf ? "Wirklich? Nochmal klicken" : "Vorlage wiederherstellen"}
      </button>
      {#if editor.speichert}<span class="te-status"><i class="fa-solid fa-circle-notch fa-spin"></i> speichert</span>{/if}
      {#if editor.fehler}<span class="te-status fehler"><i class="fa-solid fa-triangle-exclamation"></i> {editor.fehler}</span>{/if}
    </div>

    <div class="te-spalten">
      <aside class="te-katalog" aria-label="Kacheln">
        <input name="kachel-suche" class="te-suche" type="search" placeholder="Kachel suchen" bind:value={suche} />
        {#each familien as f (f.schluessel)}
          <h3>{f.titel}</h3>
          {#each f.typen as [typ, d] (typ)}
            <button class="te-typ" onclick={() => hinzufuegen(typ)} title="Hinzufügen">
              <i class="fa-solid {d.symbol} te-typ-symbol"></i>
              <span class="te-typ-text"><b>{d.titel}{#if anzahlJeTyp[typ]}<small> · {anzahlJeTyp[typ]}× gesetzt</small>{/if}</b><span>{d.beschreibung}</span></span>
              <span class="te-groessen" aria-label="Größen {d.groessen.join(', ')}">
                {#each d.groessen as g}
                  {@const [w, h] = g.split("x").map(Number)}
                  <span class="te-gz" title={g.replace("x", "×")}>{#each [0, 1, 2] as yy}{#each [0, 1, 2] as xx}<i class:f={xx < w && yy < h}></i>{/each}{/each}</span>
                {/each}
              </span>
              <i class="fa-solid fa-plus te-plus"></i>
            </button>
          {/each}
        {/each}
      </aside>

      <div class="te-mitte">
        <div class="te-rahmen" style="width: {editor.breite + 24}px">
          <div class="tel te-telefon" style="--breite: {editor.breite}px; width: {editor.breite}px" data-modus={editor.nacht ? "nacht" : undefined}>
            <div class="te-seitenkopf">{telefonKatalog.seiten.find((s) => s.schluessel === editor.seite)?.titel} · {orteState.liste.find((o) => o.slug === ort)?.name ?? ""}</div>
            <div class="raster editor" bind:this={rasterEl} style="grid-template-rows: repeat({reihen}, var(--feld))">
              {#each liste as k (k.id)}
                <div
                  class="te-k"
                  class:gewaehlt={editor.gewaehlt === k.id}
                  class:zieht={zug?.id === k.id && zug.bewegt}
                  style="grid-column: {k.x + 1} / span {k.w}; grid-row: {k.y + 1} / span {k.h}; {zug?.id === k.id && zug.bewegt ? `transform: translate(${zug.dx}px, ${zug.dy}px)` : ''}"
                  role="button"
                  tabindex="0"
                  aria-label="{telefonKatalog.typen[k.typ]?.titel} {k.w}×{k.h}"
                  onpointerdown={(e) => unten(e, k.id)}
                  onpointermove={bewegt}
                  onpointerup={los}
                  onpointercancel={los}
                  onclickcapture={(e) => e.stopPropagation()}
                  onkeydown={(e) => e.key === "Enter" && (editor.gewaehlt = k.id)}
                >
                  <Kachel kachel={k} {stand} />
                </div>
              {/each}
              {#if zug?.bewegt}
                <div class="ablage" style="--x: {zug.x}; --y: {zug.y}; --w: {zug.w}; --h: {zug.h}"></div>
              {/if}
            </div>
          </div>
        </div>
      </div>

      <aside class="te-inspektor" aria-label="Gewählte Kachel">
        {#if gewaehlt && gDef}
          <h2><i class="fa-solid {gDef.symbol}"></i> {gDef.titel}</h2>
          <p class="te-hinweis">{gDef.beschreibung}</p>
          <h3>Größe</h3>
          <div class="te-gw">
            {#each ALLE_GROESSEN as { w, h, g }}
              {@const erlaubt = gDef.groessen.includes(g)}
              <button
                class:an={gewaehlt.w === w && gewaehlt.h === h}
                disabled={!erlaubt}
                title={erlaubt ? `${w}×${h}` : "Größe für diesen Typ nicht vorgesehen"}
                onclick={() => setzeGroesse(gewaehlt.id, w, h)}
              >
                <span class="te-gz gross">{#each [0, 1, 2] as yy}{#each [0, 1, 2] as xx}<i class:f={xx < w && yy < h}></i>{/each}{/each}</span>
                {w}×{h}
              </button>
            {/each}
          </div>
          <h3>Einstellungen</h3>
          {#if gDef.einstellungen.length}
            {#each gDef.einstellungen as e (e.schluessel)}
              <div class="te-einst">
                <span class="te-einst-titel">{e.titel}</span>
                <div class="te-chips">
                  {#each e.optionen as o (o.wert)}
                    {#if e.art === "auswahl"}
                      <button class:an={einstellungWert(e) === o.wert} onclick={() => setzeEinstellung(gewaehlt.id, e.schluessel, o.wert)}>{o.titel}</button>
                    {:else}
                      <button class:an={(einstellungWert(e) as string[]).includes(o.wert)} onclick={() => umschalten(e, o.wert)}>{o.titel}</button>
                    {/if}
                  {/each}
                </div>
              </div>
            {/each}
          {:else}
            <p class="te-hinweis">{gDef.titel} hat keine Einstellungen.</p>
          {/if}
          <button class="te-weg" class:scharf={entfernenScharf} onclick={entfernen} onblur={() => (entfernenScharf = false)}>
            <i class="fa-solid fa-trash-can"></i>{entfernenScharf ? "Wirklich entfernen? Nochmal klicken" : "Entfernen"}
          </button>
        {:else}
          <h2>Keine Kachel gewählt</h2>
          <p class="te-hinweis">Klicke im Telefon auf eine Kachel, um Größe und Einstellungen zu ändern. Ziehe sie auf ein anderes Feld, um sie zu verschieben; die übrigen rücken nach.</p>
          <p class="te-hinweis">Links fügst du Kacheln hinzu. Sie landen am ersten freien Platz.</p>
        {/if}
        <p class="te-fuss"><i class="fa-solid fa-floppy-disk"></i> Änderungen werden sofort gespeichert. Am Telefon erscheinen sie beim nächsten Öffnen.</p>
      </aside>
    </div>
  </div>
</section>

<style>
  .te {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    font-size: 17px;
    color: var(--text);
  }
  .te-kopf {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 18px 24px 8px;
    flex-wrap: wrap;
  }
  .te-kopf h1 {
    margin: 0;
    font-size: 22px;
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .te-profile,
  .te-seg {
    display: inline-flex;
    gap: 4px;
    padding: 3px;
    border-radius: 12px;
    background: var(--flaeche-2);
  }
  .te-profile button,
  .te-seg button {
    border: 0;
    background: none;
    color: var(--text-2);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    min-height: 38px;
    padding: 0 14px;
    border-radius: 9px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .te-profile button.an,
  .te-seg button.an {
    background: var(--flaeche);
    color: var(--akzent-stark);
    box-shadow: var(--schatten-1);
  }
  .te-leiste {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    padding: 8px 24px 14px;
  }
  .te-feld {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    color: var(--text-2);
  }
  .te-feld select {
    font: inherit;
    font-size: 15px;
    min-height: 38px;
    padding: 0 10px;
    border-radius: 10px;
    border: 0;
    background: var(--flaeche-2);
    color: var(--text);
  }
  .te-knopf,
  .te-weg {
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    min-height: 40px;
    padding: 0 14px;
    border-radius: 10px;
    border: 0;
    background: var(--flaeche-2);
    color: var(--text);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .te-knopf.scharf,
  .te-weg.scharf {
    background: var(--gefahr-weich);
    color: var(--gefahr);
  }
  .te-status {
    font-size: 15px;
    color: var(--text-3);
  }
  .te-status.fehler {
    color: var(--gefahr);
  }
  .te-spalten {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: 320px minmax(0, 1fr) 340px;
    gap: 16px;
    padding: 0 24px 16px;
  }
  .te-katalog,
  .te-inspektor {
    overflow-y: auto;
    overflow-x: clip;
    min-height: 0;
    background: var(--flaeche);
    border-radius: 14px;
    padding: 14px;
  }
  .te-katalog h3,
  .te-inspektor h3 {
    margin: 16px 4px 8px;
    font-size: 13px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-3);
  }
  .te-suche {
    width: 100%;
    font: inherit;
    font-size: 15px;
    min-height: 40px;
    padding: 0 12px;
    border-radius: 10px;
    border: 0;
    background: var(--flaeche-2);
    color: var(--text);
  }
  .te-typ {
    width: 100%;
    display: grid;
    grid-template-columns: 26px minmax(0, 1fr) auto;
    grid-template-areas: "s t p" "s g p";
    gap: 4px 10px;
    align-items: center;
    text-align: left;
    padding: 10px;
    border: 0;
    border-radius: 12px;
    background: none;
    color: var(--text);
    font: inherit;
    cursor: pointer;
  }
  .te-typ:hover {
    background: var(--flaeche-2);
  }
  .te-typ-symbol {
    grid-area: s;
    color: var(--text-3);
    font-size: 17px;
    text-align: center;
  }
  .te-typ-text {
    grid-area: t;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .te-typ-text b {
    font-size: 17px;
  }
  .te-typ-text small {
    font-size: 13px;
    color: var(--text-3);
    font-weight: 600;
  }
  .te-typ-text span {
    font-size: 15px;
    color: var(--text-2);
  }
  .te-groessen {
    grid-area: g;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .te-plus {
    grid-area: p;
    color: var(--akzent);
  }
  .te-gz {
    display: inline-grid;
    grid-template-columns: repeat(3, 6px);
    grid-auto-rows: 6px;
    gap: 2px;
  }
  .te-gz.gross {
    grid-template-columns: repeat(3, 9px);
    grid-auto-rows: 9px;
  }
  .te-gz i {
    border-radius: 2px;
    background: var(--flaeche-3);
  }
  .te-gz i.f {
    background: var(--akzent);
  }
  .te-mitte {
    min-height: 0;
    overflow: auto;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }
  .te-rahmen {
    padding: 12px;
    border-radius: 48px;
    background: #1f2329;
    box-shadow: 0 0 0 2px #3a3f47, 0 24px 60px rgba(0, 0, 0, 0.35);
  }
  .te-telefon {
    position: relative;
    border-radius: 38px;
    overflow: hidden;
    padding: 16px 0 24px;
    min-height: 700px;
  }
  .te-seitenkopf {
    padding: 8px 12px 10px;
    font-weight: 700;
    color: var(--text-2);
    font-size: var(--s15);
  }
  .te-k {
    position: relative;
    min-width: 0;
    min-height: 0;
    cursor: grab;
    touch-action: none;
    border-radius: var(--radius);
  }
  .te-k :global(.k) {
    height: 100%;
    pointer-events: none;
  }
  .te-k.gewaehlt {
    box-shadow: 0 0 0 3px var(--akzent);
  }
  .te-k.zieht {
    z-index: 5;
    cursor: grabbing;
    opacity: 0.92;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.6), 0 0 0 3px var(--akzent);
  }
  .te-inspektor h2 {
    margin: 0 0 4px;
    font-size: 19px;
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .te-hinweis {
    margin: 6px 0;
    font-size: 15px;
    color: var(--text-2);
    line-height: 1.4;
  }
  .te-gw {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
  }
  .te-gw button {
    min-height: 64px;
    border-radius: 12px;
    border: 0;
    background: var(--flaeche-2);
    color: var(--text-2);
    font: inherit;
    font-size: 15px;
    font-weight: 700;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    cursor: pointer;
  }
  .te-gw button.an {
    background: var(--akzent-weich);
    color: var(--akzent-stark);
  }
  .te-gw button:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    background: repeating-linear-gradient(135deg, var(--flaeche-2) 0 6px, transparent 6px 12px);
  }
  .te-einst {
    margin-bottom: 12px;
  }
  .te-einst-titel {
    display: block;
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 6px 2px;
  }
  .te-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .te-chips button {
    font: inherit;
    font-size: 15px;
    min-height: 36px;
    padding: 0 12px;
    border-radius: 18px;
    border: 0;
    background: var(--flaeche-2);
    color: var(--text-2);
    cursor: pointer;
  }
  .te-chips button.an {
    background: var(--akzent-weich);
    color: var(--akzent-stark);
    font-weight: 700;
  }
  .te-weg {
    margin-top: 18px;
    width: 100%;
    justify-content: center;
    color: var(--gefahr);
  }
  .te-fuss {
    margin: 18px 2px 0;
    font-size: 15px;
    color: var(--text-3);
  }
  @media (max-width: 1280px) {
    .te-spalten {
      grid-template-columns: 280px minmax(0, 1fr) 300px;
    }
  }
  @media (max-width: 1100px) {
    .te-spalten {
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      overflow-y: auto;
    }
    .te-mitte {
      grid-column: 1 / -1;
      grid-row: 1;
    }
  }
</style>
