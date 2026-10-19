"""Ansagen der Wetterwarte vertonen (docs/WARNUNGEN.md): jeder Satz aus gemeinsam/meldungen.json einmal, mit der
Zeit-Stimme, über den Medienpool, als MP3 nach frontend/src/telefon/ansagen/klaenge/.

Aufruf aus dem Backend-Ordner (dort liegt der Katalog-Code):

    cd backend && uv run python ../tools/ansagen.py alles      # abgleichen, vertonen, exportieren, prüfen
    cd backend && uv run python ../tools/ansagen.py pruefen    # nur prüfen, ob jeder Satz einen Klang hat

Schritte einzeln: abgleich (Projekt, Rolle und Schlüssel im Medienpool), vertonen (nur Sätze ohne Klang; mit
--alle jeden neu), export (Satz auffüllen und als MP3 schreiben), gegenhoeren (jeden Klang per Spracherkennung mit
seinem Text vergleichen; einzelne Wörter verspricht die Synthese manchmal, etwa "Glätte" als "Skelette"). Einen
schwachen Satz neu sprechen lassen und die neue Fassung im Medienpool dem Satz zuweisen: Auffüllen belegt nur leere
Plätze, eine vorhandene Zuweisung bleibt. Die Sätze gehören dem Katalog: ein geänderter
Text kommt mit dem nächsten Abgleich in den Medienpool und braucht dann `vertonen --alle` für diesen Satz.
Umgebung: WETTERWARTE_MEDIENPOOL (Vorgabe http://127.0.0.1:8470), WETTERWARTE_HOEREN (Spracherkennung, Vorgabe
http://127.0.0.1:8783/v1/audio/transcriptions)."""

import difflib
import json
import os
import re
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path

from wetterwarte import ansagen

WURZEL = Path(__file__).resolve().parents[1]
MEDIENPOOL = os.environ.get("WETTERWARTE_MEDIENPOOL", "http://127.0.0.1:8470").rstrip("/")
HOEREN = os.environ.get("WETTERWARTE_HOEREN", "http://127.0.0.1:8783/v1/audio/transcriptions")
GEGENHOEREN_AB = 0.95  # Ähnlichkeit von Text und Erkanntem, darunter gilt ein Satz als verdächtig
PROJEKT = "wetterwarte"
SATZ = "klaenge"
ZIEL = WURZEL / "frontend" / "src" / "telefon" / "ansagen"  # der Medienpool schreibt nach <ZIEL>/<SATZ>/
KLAENGE = ZIEL / SATZ


def _api(pfad: str, methode: str = "GET", koerper: object = None) -> object:
    daten = json.dumps(koerper).encode() if koerper is not None else None
    anfrage = urllib.request.Request(f"{MEDIENPOOL}/api/projekte{pfad}", data=daten, method=methode,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(anfrage, timeout=120) as antwort:
            inhalt = antwort.read()
            return json.loads(inhalt) if inhalt else None
    except urllib.error.HTTPError as fehler:
        raise SystemExit(f"{methode} {pfad}: {fehler.code} {fehler.read().decode(errors='replace')[:400]}") from fehler
    except urllib.error.URLError as fehler:
        raise SystemExit(f"Medienpool unter {MEDIENPOOL} nicht erreichbar ({fehler.reason}); ./start.sh start im Medienpool-Ordner") from fehler


def _abschnitt(schluessel: str) -> str:
    k = ansagen.katalog()
    for art, klassen in k["klassen"].items():
        if any(schluessel.startswith(f"{kl['schluessel']}_") for kl in klassen):
            return {"niederschlag": "Niederschlag", "gewitter": "Gewitter", "wind": "Sturm"}[art]
    if schluessel.startswith("dwd_") or schluessel.startswith("warnung_"):
        return "Amtliche Warnungen"
    if schluessel in k["ansagen"]["saetze"]:
        return "Sätze"
    return "Zahlenreihen"


def abgleich() -> None:
    rolle = ansagen.katalog()["ansagen"]["rolle"]
    if PROJEKT not in {p["schluessel"] for p in _api("")}:  # type: ignore[union-attr]
        _api("", "POST", {"schluessel": PROJEKT, "name": "Wetterwarte", "export_ziel_klaenge": str(ZIEL)})
        print(f"Projekt {PROJEKT} angelegt")
    projekt = _api(f"/{PROJEKT}")["projekt"]  # type: ignore[index]
    export = {**projekt["export"], "klang_format": "mp3"}
    regeln = {"sprache": "german", "standard": rolle["kennung"],
              "rollen": [{"kennung": rolle["kennung"], "name": rolle["name"], "stimme": rolle["stimme"], "tempo": 1.0}]}
    _api(f"/{PROJEKT}", "PATCH", {"export_ziel_klaenge": str(ZIEL), "export": export, "ansagen": regeln})
    liste = [
        {"schluessel": s.schluessel, "name": s.text[:80], "art": "klang", "abschnitt": _abschnitt(s.schluessel),
         "ansage": s.sprechtext, "rolle": rolle["kennung"]}
        for s in ansagen.alle().values()
    ]
    ergebnis = _api(f"/{PROJEKT}/schluessel/abgleich", "POST", {"schluessel_liste": liste})
    print(f"Abgleich: {len(liste)} Sätze, neu {len(ergebnis['neu'])}, geändert {len(ergebnis['geaendert'])}, "  # type: ignore[index]
          f"überzählig {len(ergebnis['ueberzaehlig'])}")  # type: ignore[index]


def vertonen(alle: bool = False) -> None:
    stand = _api(f"/{PROJEKT}/ansagen/lauf?alle={'true' if alle else 'false'}", "POST")
    while stand["laeuft"]:  # type: ignore[index]
        print(f"\rvertont {stand['fertig']} von {stand['gesamt']}  {stand['aktuell'][:50]:50}", end="", flush=True)  # type: ignore[index]
        time.sleep(3)
        stand = _api(f"/{PROJEKT}/ansagen/lauf")
    print(f"\rvertont {stand['fertig']} von {stand['gesamt']}, ausstehend {stand['ausstehend']}{' ' * 40}")  # type: ignore[index]
    for fehler in stand["fehler"]:  # type: ignore[index]
        print(f"  Fehler: {fehler}")


def export() -> None:
    if SATZ not in {s["schluessel"] for s in _api(f"/{PROJEKT}/saetze") if s["art"] == "klang"}:  # type: ignore[union-attr]
        _api(f"/{PROJEKT}/saetze", "POST", {"schluessel": SATZ, "name": "Ansagen", "art": "klang"})
    _api(f"/{PROJEKT}/saetze/klang/{SATZ}/auffuellen", "POST")
    ergebnis = _api(f"/{PROJEKT}/saetze/klang/{SATZ}/export", "POST")
    print(f"Export: {ergebnis['klaenge_geschrieben']} Klänge nach {KLAENGE.relative_to(WURZEL)}")  # type: ignore[index]


def pruefen() -> bool:
    saetze = set(ansagen.alle())
    dateien = {p.stem for p in KLAENGE.glob("*.mp3")}
    fehlen, ueber = sorted(saetze - dateien), sorted(dateien - saetze)
    groesse = sum(p.stat().st_size for p in KLAENGE.glob("*.mp3"))
    print(f"Prüfung: {len(saetze)} Sätze, {len(dateien)} Klänge ({groesse / 1e6:.1f} MB), es fehlen {len(fehlen)}, überzählig {len(ueber)}")
    for s in fehlen[:20]:
        print(f"  fehlt: {s}")
    for s in ueber[:20]:
        print(f"  überzählig: {s}")
    return not fehlen


def _normal(text: str) -> str:
    """Kleinschreibung, ohne Satzzeichen; die Erkennung schreibt "km" für gesprochenes "Kilometer"."""
    klein = re.sub(r"\bkm\b", "kilometer", text.lower().replace("ß", "ss"))
    return " ".join(re.sub(r"[^a-zäöü0-9 ]", " ", klein).split())


def _hoeren(datei: Path) -> str:
    grenze = uuid.uuid4().hex
    koerper = (f"--{grenze}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nde\r\n--{grenze}\r\n"
               f"Content-Disposition: form-data; name=\"file\"; filename=\"{datei.name}\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode()
    koerper += datei.read_bytes() + f"\r\n--{grenze}--\r\n".encode()
    anfrage = urllib.request.Request(HOEREN, data=koerper, headers={"Content-Type": f"multipart/form-data; boundary={grenze}"})
    with urllib.request.urlopen(anfrage, timeout=180) as antwort:
        return json.loads(antwort.read()).get("text", "")


def gegenhoeren() -> None:
    """Jeden Klang erkennen lassen und mit Sprech- und Anzeigeform vergleichen (Zahlen erkennt sie als Ziffern)."""
    schwach = []
    for s in ansagen.alle().values():
        gehoert = _hoeren(KLAENGE / f"{s.schluessel}.mp3")
        guete = max(difflib.SequenceMatcher(None, _normal(gehoert), _normal(t)).ratio() for t in (s.sprechtext, s.text))
        if guete < GEGENHOEREN_AB:
            schwach.append((guete, s.schluessel, s.text, gehoert))
            print(f"  schwach {guete:.2f} {s.schluessel}: soll '{s.text}', gehört '{gehoert}'", flush=True)
    print(f"Gegenhören: {len(ansagen.alle())} Sätze, {len(schwach)} unter {GEGENHOEREN_AB:.0%} Übereinstimmung")


def main() -> None:
    befehl = sys.argv[1] if len(sys.argv) > 1 else "pruefen"
    if befehl in ("abgleich", "alles"):
        abgleich()
    if befehl in ("vertonen", "alles"):
        vertonen(alle="--alle" in sys.argv)
    if befehl in ("export", "alles"):
        export()
    if befehl == "gegenhoeren":
        gegenhoeren()
    if befehl not in ("abgleich", "vertonen", "export", "alles", "pruefen", "gegenhoeren"):
        raise SystemExit(__doc__)
    sys.exit(0 if pruefen() else 1)


if __name__ == "__main__":
    main()
