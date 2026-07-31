<script lang="ts">
  // Freischwebendes Hilfe-Fenster: ziehen, Groesse aendern, minimieren, maximieren,
  // schliessen; Inhalt aus den Markdown-Themen (hilfeThemen.ts) mit Volltextsuche
  // (global oder thema-lokal), Treffer werden markiert und in den Blick geholt.
  // Portiert aus hilfe-fenster-demo (HalloWelt42), Farben ueber unsere Tokens.
  import { untrack } from "svelte";
  import { hilfe } from "./hilfeStore.svelte";
  import { getThema, listeThemen } from "./hilfeThemen";

  const themen = listeThemen();
  const topic = $derived(hilfe.topicKey ? getThema(hilfe.topicKey) : null);

  let inhaltEl = $state<HTMLElement | null>(null);

  function markiere(container: HTMLElement, needle: string, aktivIdx: number): number {
    container.querySelectorAll("mark.tref").forEach((m) => {
      const t = document.createTextNode(m.textContent ?? "");
      m.replaceWith(t);
    });
    container.normalize();
    if (!needle) return 0;
    const nadel = needle.toLowerCase();
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
    const knoten: Node[] = [];
    while (walker.nextNode()) knoten.push(walker.currentNode);
    let zaehler = 0;
    for (const node of knoten) {
      const text = node.nodeValue ?? "";
      const low = text.toLowerCase();
      if (!low.includes(nadel)) continue;
      const frag = document.createDocumentFragment();
      let pos = 0;
      let i: number;
      while ((i = low.indexOf(nadel, pos)) !== -1) {
        if (i > pos) frag.appendChild(document.createTextNode(text.slice(pos, i)));
        const mark = document.createElement("mark");
        mark.className = "tref";
        mark.textContent = text.slice(i, i + needle.length);
        if (zaehler === aktivIdx) mark.classList.add("aktiv");
        frag.appendChild(mark);
        zaehler++;
        pos = i + needle.length;
      }
      if (pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
      node.parentNode?.replaceChild(frag, node);
    }
    const aktiv = container.querySelector("mark.tref.aktiv");
    if (aktiv) aktiv.scrollIntoView({ block: "center", behavior: "smooth" });
    return zaehler;
  }

  $effect(() => {
    void hilfe.topicKey;
    const q = hilfe.query;
    void hilfe.matchIndex;
    void hilfe.matches;
    if (!inhaltEl) return;
    markiere(inhaltEl, q.trim(), hilfe.aktivLokal());
  });

  function sichtbarkeitSichern(): void {
    if (!hilfe.open || hilfe.maximized) return;
    const w = window.innerWidth;
    const h = window.innerHeight;
    const kopf = 44;
    const unten = hilfe.minimized ? hilfe.y + kopf : hilfe.y + hilfe.height;
    const ausserhalb = hilfe.x < 0 || hilfe.y < 0 || hilfe.x + hilfe.width > w || unten > h || hilfe.width > w;
    if (ausserhalb) hilfe.maximieren();
  }

  $effect(() => {
    if (!hilfe.open) return;
    const aufRahmen = () => sichtbarkeitSichern();
    window.addEventListener("resize", aufRahmen);
    untrack(() => sichtbarkeitSichern());
    return () => window.removeEventListener("resize", aufRahmen);
  });

  function sucheTaste(e: KeyboardEvent): void {
    if (e.key === "Enter") {
      e.preventDefault();
      if (e.shiftKey) hilfe.prevMatch();
      else hilfe.nextMatch();
    }
    if (e.key === "Escape") hilfe.setQuery("");
  }

  function dragStart(e: PointerEvent): void {
    if (hilfe.maximized) return;
    e.preventDefault();
    const sx = e.clientX;
    const sy = e.clientY;
    const ox = hilfe.x;
    const oy = hilfe.y;
    function move(ev: PointerEvent): void {
      const maxX = Math.max(0, window.innerWidth - hilfe.width);
      const maxY = Math.max(0, window.innerHeight - 44);
      const nx = Math.min(maxX, Math.max(0, ox + ev.clientX - sx));
      const ny = Math.min(maxY, Math.max(0, oy + ev.clientY - sy));
      hilfe.setPosition(nx, ny);
    }
    function up(): void {
      hilfe.save();
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  }

  function resizeStart(e: PointerEvent): void {
    if (hilfe.maximized) return;
    e.preventDefault();
    e.stopPropagation();
    const sx = e.clientX;
    const sy = e.clientY;
    const ow = hilfe.width;
    const oh = hilfe.height;
    function move(ev: PointerEvent): void {
      const maxW = window.innerWidth - hilfe.x;
      const maxH = window.innerHeight - hilfe.y;
      hilfe.setSize(Math.min(ow + ev.clientX - sx, maxW), Math.min(oh + ev.clientY - sy, maxH));
    }
    function up(): void {
      hilfe.save();
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  }

  const stil = $derived(
    hilfe.maximized
      ? "inset: 70px 24px 52px 24px;"
      : `left:${hilfe.x}px; top:${hilfe.y}px; width:${hilfe.width}px; height:${hilfe.minimized ? "auto" : hilfe.height + "px"};`,
  );
</script>

{#if hilfe.open}
  <section class="hilfe-panel" style={stil} class:minimiert={hilfe.minimized}>
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <header class="hp-kopf" onpointerdown={dragStart}>
      <i class="fa-solid {topic?.icon ?? 'fa-circle-info'}"></i>
      <div class="hp-titel">
        <strong>{topic?.title ?? "Hilfe"}</strong>
        {#if topic?.subtitle}<span>{topic.subtitle}</span>{/if}
      </div>
      <div class="hp-aktionen">
        <button type="button" title="Minimieren" aria-label="Minimieren" onclick={() => hilfe.toggleMinimized()}><i class="fa-solid fa-window-minimize"></i></button>
        <button type="button" title="Maximieren" aria-label="Maximieren" onclick={() => hilfe.toggleMaximized()}><i class="fa-solid {hilfe.maximized ? 'fa-compress' : 'fa-expand'}"></i></button>
        <button type="button" title="Schließen" aria-label="Schließen" onclick={() => hilfe.close()}><i class="fa-solid fa-xmark"></i></button>
      </div>
    </header>

    {#if !hilfe.minimized}
      <div class="hp-leiste">
        <select class="hp-thema" value={hilfe.topicKey} onchange={(e) => hilfe.select(e.currentTarget.value)}>
          {#each themen as t}<option value={t.key}>{t.title}</option>{/each}
        </select>
        <div class="hp-suchzeile">
          <div class="hp-bereich" role="group" aria-label="Suchbereich">
            <button type="button" class="hp-bereich-knopf" class:aktiv={hilfe.scope === "global"} onclick={() => hilfe.setScope("global")} title="In allen Themen suchen">Alle</button>
            <button type="button" class="hp-bereich-knopf" class:aktiv={hilfe.scope === "topic"} onclick={() => hilfe.setScope("topic")} title="Nur in diesem Thema suchen">Thema</button>
          </div>
          <div class="hp-suche">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input
              placeholder={hilfe.scope === "global" ? "In allen Themen suchen ..." : "Im Thema suchen ..."}
              value={hilfe.query}
              oninput={(e) => hilfe.setQuery(e.currentTarget.value)}
              onkeydown={sucheTaste}
            />
            {#if hilfe.query.trim()}
              <span class="hp-treffer tnum">{hilfe.matchTotal ? hilfe.matchIndex + 1 : 0}/{hilfe.matchTotal}</span>
              <button type="button" title="Vorheriger" aria-label="Vorheriger Treffer" onclick={() => hilfe.prevMatch()}><i class="fa-solid fa-chevron-up"></i></button>
              <button type="button" title="Nächster" aria-label="Nächster Treffer" onclick={() => hilfe.nextMatch()}><i class="fa-solid fa-chevron-down"></i></button>
            {/if}
          </div>
        </div>
      </div>
      {#if hilfe.scope === "global" && hilfe.query.trim() && topic}
        <div class="hp-suchhinweis">Treffer in <strong>{topic.title}</strong> - mit den Pfeilen durch alle Themen.</div>
      {/if}

      <div class="hp-inhalt">
        {#if topic}
          {#key hilfe.topicKey}
            <article bind:this={inhaltEl} class="hp-artikel">{@html topic.html}</article>
          {/key}
        {:else}
          <p class="hp-leer">Kein Thema gewählt. Wähle oben eines aus.</p>
        {/if}
      </div>

      {#if !hilfe.maximized}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="hp-resize" onpointerdown={resizeStart} title="Größe ändern"></div>
      {/if}
    {/if}
  </section>
{/if}

<style>
  .hilfe-panel {
    position: fixed;
    z-index: 2000;
    display: flex;
    flex-direction: column;
    background: var(--flaeche);
    color: var(--text);
    border: 1px solid var(--rand);
    border-radius: var(--r2);
    box-shadow: var(--schatten-2);
    overflow: hidden;
    font-family: inherit;
  }
  .hp-kopf {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    cursor: move;
    background: var(--flaeche-2);
    border-bottom: 1px solid var(--rand);
  }
  .hp-kopf > i {
    color: var(--akzent);
  }
  .hp-titel {
    flex: 1;
    min-width: 0;
    line-height: 1.2;
  }
  .hp-titel strong {
    display: block;
    font-size: 14px;
  }
  .hp-titel span {
    font-size: 11px;
    color: var(--text-2);
  }
  .hp-aktionen {
    display: flex;
    gap: 2px;
  }
  .hp-aktionen button,
  .hp-suche button {
    background: transparent;
    border: 0;
    color: var(--text-2);
    cursor: pointer;
    padding: 5px 7px;
    border-radius: var(--r1);
    font-size: 12px;
  }
  .hp-aktionen button:hover,
  .hp-suche button:hover {
    background: var(--bg);
    color: var(--text);
  }
  .hp-leiste {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 8px 12px;
    border-bottom: 1px solid var(--rand);
  }
  .hp-thema {
    width: 100%;
    min-width: 0;
    background: var(--flaeche);
    color: var(--text);
    border: 1px solid var(--rand);
    border-radius: var(--r1);
    padding: 6px 8px;
    font-family: inherit;
    font-size: 12px;
  }
  .hp-suchzeile {
    display: flex;
    gap: 6px;
    align-items: stretch;
  }
  .hp-bereich {
    display: flex;
    flex-shrink: 0;
    border: 1px solid var(--rand);
    border-radius: var(--r1);
    overflow: hidden;
  }
  .hp-bereich-knopf {
    border: 0;
    background: var(--flaeche);
    color: var(--text-2);
    font-size: 11px;
    font-family: inherit;
    padding: 0 9px;
    cursor: pointer;
  }
  .hp-bereich-knopf.aktiv {
    background: var(--akzent);
    color: var(--akzent-text);
  }
  .hp-suchhinweis {
    padding: 0 12px 8px;
    font-size: 11px;
    color: var(--text-2);
    border-bottom: 1px solid var(--rand);
  }
  .hp-suche {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--flaeche);
    border: 1px solid var(--rand);
    border-radius: var(--r1);
    padding: 0 8px;
  }
  .hp-suche > i {
    color: var(--text-2);
    font-size: 12px;
  }
  .hp-suche input {
    flex: 1;
    min-width: 0;
    background: transparent;
    border: 0;
    outline: none;
    color: var(--text);
    font-family: inherit;
    font-size: 13px;
    padding: 7px 0;
  }
  .hp-treffer {
    font-size: 11px;
    color: var(--text-2);
    white-space: nowrap;
  }
  .hp-inhalt {
    flex: 1;
    overflow-y: auto;
    padding: 14px 16px;
  }
  .hp-artikel {
    font-size: 16px;
    line-height: 1.65;
  }
  .hp-leer {
    color: var(--text-2);
    font-size: 13px;
  }
  .hp-resize {
    position: absolute;
    right: 0;
    bottom: 0;
    width: 16px;
    height: 16px;
    cursor: nwse-resize;
    background: linear-gradient(135deg, transparent 50%, var(--rand-stark) 50%);
  }

  .hp-artikel :global(h1),
  .hp-artikel :global(h2),
  .hp-artikel :global(h3) {
    font-size: 18.5px;
    margin: 16px 0 7px;
    color: var(--text);
  }
  .hp-artikel :global(p) {
    margin: 0 0 10px;
  }
  .hp-artikel :global(ul),
  .hp-artikel :global(ol) {
    margin: 0 0 10px;
    padding-left: 20px;
  }
  .hp-artikel :global(li) {
    margin: 3px 0;
  }
  .hp-artikel :global(code) {
    background: var(--bg);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 14px;
  }
  .hp-artikel :global(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0;
    font-size: 14.5px;
  }
  .hp-artikel :global(th),
  .hp-artikel :global(td) {
    border: 1px solid var(--rand);
    padding: 5px 8px;
    text-align: left;
  }
  .hp-artikel :global(a) {
    color: var(--akzent);
  }
  .hp-artikel :global(mark.tref) {
    background: #fde68a;
    color: #1f2933;
    border-radius: 2px;
  }
  .hp-artikel :global(mark.tref.aktiv) {
    background: #f59e0b;
    outline: 2px solid #f59e0b;
  }
</style>
