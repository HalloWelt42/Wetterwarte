#!/usr/bin/env python3
"""Leitet aus frontend/public/symbol.svg den Symbolsatz für Browser-Tabs, Startbildschirm und PWA ab
(Vorlage des Appkerns, tools/symbole.py).

Einzige Quelle ist symbol.svg: ein Rechteck über die ganze Fläche als Grund, danach das Motiv. Erzeugt in
frontend/public:
  favicon.svg                                   Kopie der Quelle für moderne Browser
  favicon.ico                                   16, 32 und 48 in einer Datei
  favicon-32.png                                wie die Quelle, mit durchsichtigen Ecken (Tab im Browser)
  icon-192.png, icon-512.png                    Grund randlos und deckend (purpose any; iOS 18 nimmt für den
                                                Startbildschirm diese aus dem Manifest, nicht das apple-touch-icon,
                                                und zeigt mit durchsichtigen Ecken kein Symbol; die Ecken rundet
                                                das Gerät selbst)
  icon-maskable-192.png, icon-maskable-512.png  Grund randlos, Motiv in der sicheren Zone (purpose maskable)
  apple-touch-icon.png                          180, Grund randlos und deckend

Die Bilder liegen im Repo und werden nie zur Laufzeit erzeugt. Nach einer Änderung an symbol.svg neu erzeugen:
  python3 tools/symbole.py
Braucht cairosvg (mit der Cairo-Bibliothek, auf dem Mac aus Homebrew) und Pillow, nur auf dem Rechner, der die
Bilder erzeugt.
"""

from __future__ import annotations

import io
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image

OEFFENTLICH = Path(__file__).resolve().parent.parent / "frontend" / "public"
QUELLE = OEFFENTLICH / "symbol.svg"
SVG = "http://www.w3.org/2000/svg"
# Anteil des Motivs am maskierbaren Symbol: alles bleibt im Kreis mit 80 % Durchmesser, den kein Gerät beschneidet
SICHERE_ZONE = 0.66


def rastern(svg: bytes, groesse: int) -> Image.Image:
    png = cairosvg.svg2png(bytestring=svg, output_width=groesse, output_height=groesse)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def randlos(svg: bytes, anteil: float) -> bytes:
    """Grund ohne runde Ecken über die ganze Fläche, Motiv um die Mitte auf anteil verkleinert."""
    ET.register_namespace("", SVG)
    wurzel = ET.fromstring(svg)
    _, _, breite, hoehe = (float(z) for z in wurzel.get("viewBox", "").split())
    grund = next((k for k in wurzel if k.tag == f"{{{SVG}}}rect" and float(k.get("width", 0)) == breite
                  and float(k.get("height", 0)) == hoehe), None)
    if grund is None:
        sys.exit(f"{QUELLE}: Rechteck über die ganze Fläche (Grund) fehlt")
    grund.attrib.pop("rx", None)
    grund.attrib.pop("ry", None)
    if anteil != 1:
        motiv = [k for k in wurzel if k is not grund and k.tag != f"{{{SVG}}}defs"]
        x, y = breite / 2, hoehe / 2
        gruppe = ET.SubElement(wurzel, f"{{{SVG}}}g", transform=f"translate({x:g} {y:g}) scale({anteil}) translate({-x:g} {-y:g})")
        for k in motiv:
            wurzel.remove(k)
            gruppe.append(k)
    return ET.tostring(wurzel)


def deckend(svg: bytes, groesse: int) -> Image.Image:
    return rastern(svg, groesse).convert("RGB")


def main() -> None:
    quelle = QUELLE.read_bytes()
    shutil.copyfile(QUELLE, OEFFENTLICH / "favicon.svg")

    ico = [rastern(quelle, g) for g in (48, 32, 16)]
    ico[0].save(OEFFENTLICH / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[1:])
    rastern(quelle, 32).save(OEFFENTLICH / "favicon-32.png", optimize=True)
    voll, rand = randlos(quelle, 1), randlos(quelle, SICHERE_ZONE)
    for groesse in (192, 512):
        deckend(voll, groesse).save(OEFFENTLICH / f"icon-{groesse}.png", optimize=True)
        deckend(rand, groesse).save(OEFFENTLICH / f"icon-maskable-{groesse}.png", optimize=True)
    deckend(voll, 180).save(OEFFENTLICH / "apple-touch-icon.png", optimize=True)
    print(f"Symbolsatz aus {QUELLE.name} erzeugt in {OEFFENTLICH}")


if __name__ == "__main__":
    main()
