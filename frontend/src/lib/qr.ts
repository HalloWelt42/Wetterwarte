// Kleiner QR-Helfer: erzeugt aus einem Text ein skalierbares SVG (rein lokal,
// ohne Netz). Genutzt fuer Krypto-Adressen und den Ko-fi-Link im Danke-Overlay.
import qrcode from "qrcode-generator";

export function qrSvg(text: string): string {
  // Fehlerkorrektur M ist ein guter Kompromiss aus Groesse und Robustheit;
  // Typ 0 waehlt die Version automatisch passend zur Datenmenge.
  const qr = qrcode(0, "M");
  qr.addData(text);
  qr.make();
  // scalable: viewBox statt fester Pixelgroesse - Groesse steuert das CSS.
  return qr.createSvgTag({ cellSize: 4, margin: 0, scalable: true });
}
