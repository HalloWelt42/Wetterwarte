// Mikrodiagramme der Telefonansicht (Entwurf). Jedes Element mit data-mikro="art" bekommt ein SVG in
// seiner tatsächlichen Größe; bei Größenänderung wird neu gezeichnet. Farben kommen aus den CSS-Variablen
// der Telefonansicht, dadurch stimmt auch der Nachtbetrieb ohne Sonderfall. Diese Geometrie ist die Vorlage
// für die späteren Svelte-Bausteine (ein Baustein je Art, gleiche Parameter).
(() => {
  const NS = "http://www.w3.org/2000/svg";

  const zahlen = (s) => (s || "").split(",").filter((x) => x.trim() !== "").map(Number);
  const farbe = (el, name) => getComputedStyle(el).getPropertyValue(name).trim() || name;
  const tempStufe = (v) =>
    v <= -5 ? "--t-frost" : v <= 2 ? "--t-kalt" : v <= 8 ? "--t-kuehl" : v <= 15 ? "--t-mild" : v <= 24 ? "--t-warm" : v <= 30 ? "--t-heiss" : "--t-extrem";
  const minuten = (s) => {
    const [h, m] = s.split(":").map(Number);
    return h * 60 + m;
  };

  function knoten(name, attr, eltern) {
    const k = document.createElementNS(NS, name);
    for (const [a, w] of Object.entries(attr)) k.setAttribute(a, w);
    if (eltern) eltern.appendChild(k);
    return k;
  }
  function text(eltern, x, y, inhalt, anker = "middle", klasse = "") {
    const t = knoten("text", { x, y, "text-anchor": anker, class: klasse }, eltern);
    t.textContent = inhalt;
    return t;
  }

  // Glatte Linie durch Punkte (monotone kubische Interpolation, kein Überschwingen)
  function pfad(p) {
    if (p.length < 2) return "";
    const n = p.length;
    const d = [];
    const m = [];
    for (let i = 0; i < n - 1; i++) d.push((p[i + 1][1] - p[i][1]) / (p[i + 1][0] - p[i][0]));
    m[0] = d[0];
    m[n - 1] = d[n - 2];
    for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
    let s = `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}`;
    for (let i = 0; i < n - 1; i++) {
      const h = (p[i + 1][0] - p[i][0]) / 3;
      s += ` C${(p[i][0] + h).toFixed(1)},${(p[i][1] + m[i] * h).toFixed(1)} ${(p[i + 1][0] - h).toFixed(1)},${(p[i + 1][1] - m[i + 1] * h).toFixed(1)} ${p[i + 1][0].toFixed(1)},${p[i + 1][1].toFixed(1)}`;
    }
    return s;
  }

  const ARTEN = {
    // Verlaufslinie: data-werte, data-farbe (CSS-Variable oder "temp"), data-flaeche, data-jetzt (Index),
    // data-beschriften (jeden n-ten Wert beschriften), data-minmax (Tief und Hoch markieren),
    // data-einheit (hinter beschrifteten Werten, Standard "°", leer für ohne)
    linie(el, svg, b, h) {
      const w = zahlen(el.dataset.werte);
      const einheit = el.dataset.einheit ?? "°";
      const lo = Math.min(...w), hi = Math.max(...w);
      const spanne = hi - lo || 1;
      const oben = el.dataset.beschriften || el.dataset.minmax ? 18 : 4;
      const unten = el.dataset.minmax ? 16 : 4;
      const x = (i) => 4 + (i * (b - 8)) / (w.length - 1);
      const y = (v) => oben + (1 - (v - lo) / spanne) * (h - oben - unten);
      const punkte = w.map((v, i) => [x(i), y(v)]);
      let strich = farbe(el, el.dataset.farbe || "--akzent");
      if (el.dataset.farbe === "temp") {
        const id = "v" + Math.random().toString(36).slice(2);
        const g = knoten("linearGradient", { id, x1: 0, y1: y(lo), x2: 0, y2: y(hi), gradientUnits: "userSpaceOnUse" }, knoten("defs", {}, svg));
        for (let s = 0; s <= 4; s++) {
          const v = lo + (s / 4) * spanne;
          knoten("stop", { offset: s / 4, "stop-color": farbe(el, tempStufe(v)) }, g);
        }
        strich = `url(#${id})`;
      }
      if (el.dataset.flaeche) {
        const f = knoten("path", { d: pfad(punkte) + ` L${x(w.length - 1)},${h} L${x(0)},${h} Z`, fill: strich, opacity: 0.16 }, svg);
        f.setAttribute("fill", el.dataset.farbe === "temp" ? farbe(el, "--t-mild") : strich);
      }
      knoten("path", { d: pfad(punkte), fill: "none", stroke: strich, "stroke-width": 2.6, "stroke-linecap": "round" }, svg);
      const n = Number(el.dataset.beschriften || 0);
      if (n) w.forEach((v, i) => i % n === 0 && text(svg, x(i), y(v) - 7, `${Math.round(v)}${einheit}`, "middle", "hell"));
      if (el.dataset.minmax) {
        const iHi = w.indexOf(hi), iLo = w.indexOf(lo);
        text(svg, Math.min(Math.max(x(iHi), 14), b - 14), y(hi) - 6, `${Math.round(hi)}${einheit}`, "middle", "hell");
        text(svg, Math.min(Math.max(x(iLo), 14), b - 14), y(lo) + 15, `${Math.round(lo)}${einheit}`, "middle");
      }
      const j = el.dataset.jetzt === undefined ? w.length - 1 : Number(el.dataset.jetzt);
      if (j >= 0) {
        knoten("circle", { cx: x(j), cy: y(w[j]), r: 5, fill: farbe(el, "--text"), stroke: farbe(el, "--flaeche"), "stroke-width": 2.5 }, svg);
      }
    },

    // Säulen: data-werte, data-max, data-farbe, data-jetzt (hervorgehobener Index), data-achse ("a|b|c")
    balken(el, svg, b, h) {
      const w = zahlen(el.dataset.werte);
      const max = Number(el.dataset.max) || Math.max(...w, 1);
      const achse = el.dataset.achse ? el.dataset.achse.split("|") : null;
      const unten = achse ? 16 : 0;
      const luecke = w.length > 16 ? 2 : 3;
      const sb = (b - luecke * (w.length - 1)) / w.length;
      const f = farbe(el, el.dataset.farbe || "--regen");
      knoten("rect", { x: 0, y: h - unten - 1, width: b, height: 1, fill: farbe(el, "--flaeche-3") }, svg);
      w.forEach((v, i) => {
        const bh = Math.max(v > 0 ? 3 : 0, (v / max) * (h - unten - 2));
        knoten("rect", { x: i * (sb + luecke), y: h - unten - bh, width: sb, height: bh, rx: Math.min(2.5, sb / 2), fill: f, opacity: el.dataset.jetzt && Number(el.dataset.jetzt) !== i ? 0.55 : 1 }, svg);
      });
      if (achse) achse.forEach((a, i) => text(svg, (i * b) / (achse.length - 1), h - 2, a, i === 0 ? "start" : i === achse.length - 1 ? "end" : "middle"));
    },

    // Bogen (270 Grad) mit Farbskala und Marke: data-wert, data-max, data-skala ("uv" | "luft")
    bogen(el, svg, b, h) {
      const wert = Number(el.dataset.wert), max = Number(el.dataset.max) || 11;
      const r = Math.min(b, h * 1.18) / 2 - 7;
      const cx = b / 2, cy = r + 6;
      const start = 135, bogen = 270;
      const punkt = (grad) => [cx + r * Math.cos((grad * Math.PI) / 180), cy + r * Math.sin((grad * Math.PI) / 180)];
      const skala = el.dataset.skala === "luft" ? ["--gut", "--w1", "--w2", "--w3", "--w4"] : ["--gut", "--w1", "--w2", "--w3", "--w4"];
      const teile = skala.length;
      for (let i = 0; i < teile; i++) {
        const a = start + (i * bogen) / teile + 1.5, e = start + ((i + 1) * bogen) / teile - 1.5;
        const [x1, y1] = punkt(a), [x2, y2] = punkt(e);
        knoten("path", { d: `M${x1},${y1} A${r},${r} 0 0 1 ${x2},${y2}`, fill: "none", stroke: farbe(el, skala[i]), "stroke-width": 7, "stroke-linecap": "round", opacity: 0.9 }, svg);
      }
      const [mx, my] = punkt(start + (Math.min(wert, max) / max) * bogen);
      knoten("circle", { cx: mx, cy: my, r: 7, fill: farbe(el, "--text"), stroke: farbe(el, "--flaeche"), "stroke-width": 3 }, svg);
    },

    // Vollkreis-Anteil: data-wert, data-max, data-farbe
    ring(el, svg, b, h) {
      const wert = Number(el.dataset.wert), max = Number(el.dataset.max) || 100;
      const r = Math.min(b, h) / 2 - 5;
      const u = 2 * Math.PI * r;
      knoten("circle", { cx: b / 2, cy: h / 2, r, fill: "none", stroke: farbe(el, "--flaeche-3"), "stroke-width": 7 }, svg);
      knoten("circle", { cx: b / 2, cy: h / 2, r, fill: "none", stroke: farbe(el, el.dataset.farbe || "--akzent"), "stroke-width": 7, "stroke-linecap": "round", "stroke-dasharray": `${(u * Math.min(wert, max)) / max} ${u}`, transform: `rotate(-90 ${b / 2} ${h / 2})` }, svg);
    },

    // Windrose: data-grad (woher der Wind kommt, 0 = Nord), data-staerke (0..1 für die Pfeillänge)
    kompass(el, svg, b, h) {
      const grad = Number(el.dataset.grad), r = Math.min(b, h) / 2 - 3;
      const cx = b / 2, cy = h / 2;
      knoten("circle", { cx, cy, r, fill: "none", stroke: farbe(el, "--flaeche-3"), "stroke-width": 2 }, svg);
      for (let i = 0; i < 12; i++) {
        const a = (i * 30 * Math.PI) / 180, l = i % 3 === 0 ? 8 : 4;
        knoten("line", { x1: cx + Math.sin(a) * r, y1: cy - Math.cos(a) * r, x2: cx + Math.sin(a) * (r - l), y2: cy - Math.cos(a) * (r - l), stroke: farbe(el, i % 3 === 0 ? "--text-3" : "--flaeche-3"), "stroke-width": 2 }, svg);
      }
      if (r > 40) {
        text(svg, cx, cy - r + 22, "N", "middle", "hell");
      }
      // Pfeil zeigt, wohin der Wind weht
      const ziel = ((grad + 180) * Math.PI) / 180;
      const lang = r * 0.78;
      const g = knoten("g", { transform: `rotate(${grad + 180} ${cx} ${cy})` }, svg);
      knoten("line", { x1: cx, y1: cy + lang * 0.7, x2: cx, y2: cy - lang + 10, stroke: farbe(el, "--text"), "stroke-width": 3.2, "stroke-linecap": "round" }, g);
      knoten("path", { d: `M${cx - 8},${cy - lang + 14} L${cx},${cy - lang} L${cx + 8},${cy - lang + 14} Z`, fill: farbe(el, "--text") }, g);
      void ziel;
    },

    // Sonnenbogen: data-auf, data-unter, data-jetzt (HH:MM), data-beschriften
    sonne(el, svg, b, h) {
      const auf = minuten(el.dataset.auf), unter = minuten(el.dataset.unter), jetzt = minuten(el.dataset.jetzt);
      const unten = el.dataset.beschriften ? 18 : 4;
      const hor = h - unten - 2;
      const rx = b / 2 - 10, ry = Math.min(hor - 8, rx * 0.9);
      const cx = b / 2;
      knoten("line", { x1: 0, y1: hor, x2: b, y2: hor, stroke: farbe(el, "--flaeche-3"), "stroke-width": 2 }, svg);
      knoten("path", { d: `M${cx - rx},${hor} A${rx},${ry} 0 0 1 ${cx + rx},${hor}`, fill: "none", stroke: farbe(el, "--flaeche-3"), "stroke-width": 2.5, "stroke-dasharray": "4 5" }, svg);
      const t = Math.max(0, Math.min(1, (jetzt - auf) / (unter - auf)));
      const a = Math.PI * (1 - t);
      const sx = cx + rx * Math.cos(a), sy = hor - ry * Math.sin(a);
      if (jetzt > auf && jetzt < unter) {
        const id = "s" + Math.random().toString(36).slice(2);
        const clip = knoten("clipPath", { id }, knoten("defs", {}, svg));
        knoten("rect", { x: 0, y: 0, width: sx, height: hor }, clip);
        knoten("path", { d: `M${cx - rx},${hor} A${rx},${ry} 0 0 1 ${cx + rx},${hor}`, fill: "none", stroke: farbe(el, "--sonne"), "stroke-width": 3, "clip-path": `url(#${id})` }, svg);
        knoten("circle", { cx: sx, cy: sy, r: 8, fill: farbe(el, "--sonne") }, svg);
      }
      if (el.dataset.beschriften) {
        text(svg, 2, h - 2, el.dataset.auf, "start", "hell");
        text(svg, b - 2, h - 2, el.dataset.unter, "end", "hell");
      }
    },

    // Mondscheibe: data-anteil (0..1 beleuchtet), data-zunehmend ("1" rechts hell)
    mond(el, svg, b, h) {
      const k = Number(el.dataset.anteil), zun = el.dataset.zunehmend === "1";
      const r = Math.min(b, h) / 2 - 2, cx = b / 2, cy = h / 2;
      knoten("circle", { cx, cy, r, fill: farbe(el, "--flaeche-3") }, svg);
      // Licht: Halbkreis plus Ellipse mit Radius |1-2k| * r
      const e = Math.abs(1 - 2 * k) * r;
      const seite = zun ? 1 : 0;
      const bauch = k > 0.5 ? seite : 1 - seite;
      const d = `M${cx},${cy - r} A${r},${r} 0 0 ${seite} ${cx},${cy + r} A${e},${r} 0 0 ${bauch} ${cx},${cy - r} Z`;
      knoten("path", { d, fill: farbe(el, "--text") , opacity: 0.92 }, svg);
    },

    // Abweichung vom Normalwert: data-werte (+/-), data-jetzt (Index), data-achse
    abweichung(el, svg, b, h) {
      const w = zahlen(el.dataset.werte);
      const achse = el.dataset.achse ? el.dataset.achse.split("|") : null;
      const unten = achse ? 16 : 0;
      const max = Math.max(...w.map(Math.abs), 0.5);
      const mitte = (h - unten) / 2;
      const luecke = 3, sb = (b - luecke * (w.length - 1)) / w.length;
      knoten("rect", { x: 0, y: mitte - 0.5, width: b, height: 1, fill: farbe(el, "--flaeche-3") }, svg);
      const j = el.dataset.jetzt === undefined ? -1 : Number(el.dataset.jetzt);
      w.forEach((v, i) => {
        if (Number.isNaN(v)) return;
        const bh = Math.max(2, (Math.abs(v) / max) * (mitte - 2));
        knoten("rect", { x: i * (sb + luecke), y: v >= 0 ? mitte - bh : mitte, width: sb, height: bh, rx: 2, fill: farbe(el, v >= 0 ? "--t-heiss" : "--t-frost"), opacity: j === -1 || i === j ? 1 : 0.5 }, svg);
      });
      if (achse) achse.forEach((a, i) => text(svg, (i * b) / (achse.length - 1), h - 2, a, i === 0 ? "start" : i === achse.length - 1 ? "end" : "middle"));
    },

    // Blitze in Entfernungsringen: data-punkte ("km:grad,..."), data-max (km), data-ringe ("10,25,50")
    ringe(el, svg, b, h) {
      const max = Number(el.dataset.max) || 50;
      const ringe = zahlen(el.dataset.ringe || "10,25,50");
      const r = Math.min(b, h) / 2 - 2, cx = b / 2, cy = h / 2;
      ringe.forEach((km) => knoten("circle", { cx, cy, r: (km / max) * r, fill: "none", stroke: farbe(el, "--flaeche-3"), "stroke-width": 1.5 }, svg));
      if (r > 50) ringe.forEach((km) => text(svg, cx + 4, cy - (km / max) * r + 14, `${km}`, "start"));
      knoten("circle", { cx, cy, r: 4, fill: farbe(el, "--akzent") }, svg);
      (el.dataset.punkte || "").split(",").filter(Boolean).forEach((p, i) => {
        const [km, grad] = p.split(":").map(Number);
        const a = (grad * Math.PI) / 180, d = (Math.min(km, max) / max) * r;
        knoten("circle", { cx: cx + Math.sin(a) * d, cy: cy - Math.cos(a) * d, r: i < 3 ? 4.5 : 3, fill: farbe(el, "--w1"), opacity: i < 3 ? 1 : 0.6 }, svg);
      });
    },
  };

  function zeichne(el) {
    const art = ARTEN[el.dataset.mikro];
    if (!art) return;
    const b = el.clientWidth, h = el.clientHeight;
    if (!b || !h) return;
    el.querySelector(":scope > svg.mikro")?.remove();
    const svg = knoten("svg", { class: "mikro", viewBox: `0 0 ${b} ${h}`, width: b, height: h });
    el.appendChild(svg);
    art(el, svg, b, h);
  }

  function alle() {
    document.querySelectorAll("[data-mikro]").forEach(zeichne);
  }
  const beobachter = new ResizeObserver((eintraege) => eintraege.forEach((e) => zeichne(e.target)));
  function start() {
    document.querySelectorAll("[data-mikro]").forEach((el) => beobachter.observe(el));
    alle();
  }
  window.mikroNeu = alle; // nach Umschalten (Nachtbetrieb, Schriftstufe) neu einfärben
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
  document.fonts?.ready.then(alle);
})();
