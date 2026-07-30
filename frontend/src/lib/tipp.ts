// Eigene Hover-Erklaerung (kein natives title-Attribut). Zeigt beim Ueberfahren
// eine kleine Blase mit dem erklaerenden Text; verwendbar als use:tipp={"..."}.
let blase: HTMLDivElement | null = null;

function entferne(): void {
  blase?.remove();
  blase = null;
}

function zeige(text: string, el: HTMLElement): void {
  entferne();
  blase = document.createElement("div");
  blase.className = "tipp-blase";
  blase.textContent = text;
  document.body.appendChild(blase);
  const r = el.getBoundingClientRect();
  const bb = blase.getBoundingClientRect();
  let links = r.left + r.width / 2 - bb.width / 2;
  links = Math.max(8, Math.min(links, window.innerWidth - bb.width - 8));
  let oben = r.top - bb.height - 8;
  if (oben < 8) oben = r.bottom + 8;
  blase.style.left = `${links}px`;
  blase.style.top = `${oben}px`;
  requestAnimationFrame(() => blase?.classList.add("sichtbar"));
}

export function tipp(node: HTMLElement, text: string) {
  let aktuell = text;
  const ein = () => aktuell && zeige(aktuell, node);
  const aus = () => entferne();
  node.classList.add("hat-tipp");
  node.addEventListener("mouseenter", ein);
  node.addEventListener("mouseleave", aus);
  node.addEventListener("focus", ein);
  node.addEventListener("blur", aus);
  return {
    update(neu: string) {
      aktuell = neu;
    },
    destroy() {
      node.removeEventListener("mouseenter", ein);
      node.removeEventListener("mouseleave", aus);
      node.removeEventListener("focus", ein);
      node.removeEventListener("blur", aus);
      entferne();
    },
  };
}
