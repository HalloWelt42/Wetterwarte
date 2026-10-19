// Entwurfsleiste der Telefonseiten: Galerie, Schriftstufe und Nachtbetrieb zum Durchprobieren.
// Gehört nur zum Entwurf, nicht zur App (dort sitzen Stufe und Nachtbetrieb unter "Mehr").
(() => {
  const STUFEN = [
    ["normal", "Aa"],
    ["gross", "Aa+"],
    ["sehr-gross", "Aa++"],
  ];
  const geraete = () => document.querySelectorAll(".tel");
  const leiste = document.createElement("div");
  leiste.className = "mock-leiste";
  leiste.innerHTML =
    `<a href="/mockups/index.html"><i class="fa-solid fa-table-cells"></i> Galerie</a>` +
    STUFEN.map(([s, t]) => `<button data-stufe-knopf="${s}" title="Schriftstufe">${t}</button>`).join("") +
    `<button data-nacht-knopf title="Nachtbetrieb"><i class="fa-solid fa-moon"></i> Nacht</button>`;
  document.body.appendChild(leiste);

  function setzeStufe(s) {
    geraete().forEach((g) => (s === "normal" ? g.removeAttribute("data-stufe") : g.setAttribute("data-stufe", s)));
    leiste.querySelectorAll("[data-stufe-knopf]").forEach((k) => k.classList.toggle("an", k.dataset.stufeKnopf === s));
    window.mikroNeu?.();
  }
  function setzeNacht(an) {
    geraete().forEach((g) => (an ? g.setAttribute("data-modus", "nacht") : g.removeAttribute("data-modus")));
    leiste.querySelector("[data-nacht-knopf]").classList.toggle("an", an);
    // Nachtbetrieb: farbige Symbole gegen einfarbige Masken tauschen. Die Maske bekommt nur Klasse
    // und Bild; ihre Größe kommt wie beim Bild aus dem Stylesheet, damit ein Wechsel der
    // Schriftstufe im Nachtbetrieb nichts verschiebt.
    document.querySelectorAll(".tel img.mc").forEach((img) => {
      if (an) {
        const m = document.createElement("span");
        m.className = img.className.replace(/\bmc\b/, "mc mcm");
        m.style.setProperty("--i", `url(${img.src.replace("/fill/", "/monochrome/")})`);
        m.dataset.quelle = img.src;
        img.replaceWith(m);
      }
    });
    if (!an)
      document.querySelectorAll(".tel span.mcm[data-quelle]").forEach((m) => {
        const img = document.createElement("img");
        img.className = m.className.replace(/\s*mcm\b/, "");
        img.src = m.dataset.quelle;
        img.alt = "";
        m.replaceWith(img);
      });
    window.mikroNeu?.();
  }
  leiste.querySelectorAll("[data-stufe-knopf]").forEach((k) => (k.onclick = () => setzeStufe(k.dataset.stufeKnopf)));
  const nacht = leiste.querySelector("[data-nacht-knopf]");
  nacht.onclick = () => setzeNacht(!nacht.classList.contains("an"));
  setzeStufe("normal");
  if (document.querySelector('.tel[data-modus="nacht"]')) setzeNacht(true);
})();
