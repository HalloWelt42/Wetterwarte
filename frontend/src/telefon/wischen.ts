// Waagerechtes Wischen erkennen, ohne das senkrechte Rollen zu stören: zählt nur, wenn die
// Bewegung klar waagerecht und lang genug ist. Aktion für Svelte: use:wischen={{ links, rechts }}.
export function wischen(el: HTMLElement, aktionen: { links?: () => void; rechts?: () => void }) {
  let start: { x: number; y: number; t: number } | null = null;
  const unten = (e: PointerEvent) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    start = { x: e.clientX, y: e.clientY, t: e.timeStamp };
  };
  const oben = (e: PointerEvent) => {
    if (!start) return;
    const dx = e.clientX - start.x;
    const dy = e.clientY - start.y;
    const schnell = e.timeStamp - start.t < 600;
    start = null;
    if (!schnell || Math.abs(dx) < 70 || Math.abs(dx) < 2 * Math.abs(dy)) return;
    if (dx < 0) aktionen.links?.();
    else aktionen.rechts?.();
  };
  const weg = () => (start = null);
  el.addEventListener("pointerdown", unten);
  el.addEventListener("pointerup", oben);
  el.addEventListener("pointercancel", weg);
  return {
    update(neu: typeof aktionen) {
      aktionen = neu;
    },
    destroy() {
      el.removeEventListener("pointerdown", unten);
      el.removeEventListener("pointerup", oben);
      el.removeEventListener("pointercancel", weg);
    },
  };
}
