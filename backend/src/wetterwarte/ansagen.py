"""Sätze der Meldungen aus gemeinsam/meldungen.json (siehe docs/WARNUNGEN.md).

Jeder Satz hat einen Schlüssel, eine Anzeigeform mit Ziffern und eine Sprechform mit ausgeschriebenen Zahlen.
Eine Meldung ist eine Folge von Satzschlüsseln: ihr Text ist die Verkettung der Anzeigeformen, ihre Ansage die
Folge der vertonten Klänge. `alle()` zählt jeden Satz genau einmal auf (für die Vertonung und die Prüfung)."""

import re
from dataclasses import dataclass
from datetime import datetime
from functools import cache

from .gemeinsam import lies


@dataclass(frozen=True)
class Satz:
    schluessel: str
    text: str
    sprechtext: str


_EINER = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf",
          "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
_ZEHNER = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]


def zahlwort(n: int) -> str:
    """Ganze Zahl von 0 bis 999 als deutsches Zahlwort ("fünfundneunzig", "hundertzwanzig")."""
    if not 0 <= n < 1000:
        raise ValueError(f"Zahl außerhalb 0 bis 999: {n}")
    if n < 20:
        return _EINER[n]
    if n < 100:
        einer, zehner = n % 10, n // 10
        return _ZEHNER[zehner] if not einer else f"{'ein' if einer == 1 else _EINER[einer]}und{_ZEHNER[zehner]}"
    hunderter, rest = divmod(n, 100)
    vorne = "hundert" if hunderter == 1 else f"{_EINER[hunderter]}hundert"
    return vorne + (zahlwort(rest) if rest else "")


def sprechform(text: str) -> str:
    """Ziffern ausschreiben, "1 Uhr" als "ein Uhr"."""
    def wort(m: re.Match[str]) -> str:
        return "ein" if m.group() == "1" and text[m.end() :].startswith(" Uhr") else zahlwort(int(m.group()))

    return re.sub(r"\d+", wort, text)


def kennung(name: str) -> str:
    """ASCII-Kennung eines Namens (\"Schwere Sturmböen\" -> \"schwere_sturmboeen\")."""
    klein = name.lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    return re.sub(r"[^a-z0-9]+", "_", klein).strip("_")


def katalog() -> dict:
    return lies("meldungen.json")


def _reihe(r: dict) -> list[int]:
    return list(r["werte"]) if "werte" in r else list(range(r["von"], r["bis"] + 1, r.get("schritt", 1)))


@cache
def alle() -> dict[str, Satz]:
    """Jeder Satz des Katalogs genau einmal, nach Schlüssel."""
    k = katalog()
    a = k["ansagen"]
    saetze: dict[str, Satz] = {}

    def neu(schluessel: str, text: str) -> None:
        if schluessel in saetze:
            raise ValueError(f"Satzschlüssel doppelt: {schluessel}")
        saetze[schluessel] = Satz(schluessel, text, sprechform(text))

    for klassen in k["klassen"].values():
        for klasse in klassen:
            for z in a["zeiten"]:
                neu(f"{klasse['schluessel']}_{z['min']}", klasse["satz"].replace("{zeit}", z["text"]))
    for name, r in a["reihen"].items():
        for n in _reihe(r):
            neu(f"{name}_{n}", r["muster"].replace("{zahl}", str(n)))
        if "nah" in r:
            neu(f"{name}_nah", r["nah"]["text"])
    for schluessel, text in a["saetze"].items():
        neu(schluessel, text)
    for ereignis in a["dwd"]:
        neu(f"dwd_{kennung(ereignis)}", f"{ereignis}.")
    return saetze


def text(bausteine: list[str]) -> str:
    """Anzeigetext einer Meldung aus ihren Satzschlüsseln."""
    saetze = alle()
    return " ".join(saetze[b].text for b in bausteine)


# --- Bausteine nach Art --------------------------------------------------------------------------------------


def zeit(minuten: float) -> dict:
    """Nächste Zeitangabe der Liste ("in 30 Minuten"); unter zehn Minuten "in wenigen Minuten"."""
    zeiten = katalog()["ansagen"]["zeiten"]
    if minuten < 10:
        return zeiten[0]
    return min(zeiten[1:], key=lambda z: (abs(z["min"] - minuten), z["min"]))


def klasse(art: str, schluessel: str) -> dict:
    return next(k for k in katalog()["klassen"][art] if k["schluessel"] == schluessel)


def kernsatz(klasse_schluessel: str, minuten: float) -> str:
    return f"{klasse_schluessel}_{zeit(minuten)['min']}"


def boeen(kmh: float) -> str:
    r = katalog()["ansagen"]["reihen"]["boeen"]
    gerundet = int(round(kmh / r["schritt"]) * r["schritt"])
    return f"boeen_{min(r['bis'], max(r['von'], gerundet))}"


def blitze(km: float) -> str:
    r = katalog()["ansagen"]["reihen"]["blitze"]
    if km <= r["nah"]["bis_km"]:
        return "blitze_nah"
    return f"blitze_{min(r['werte'], key=lambda w: (abs(w - km), w))}"


def dwd(ereignis: str) -> str:
    """Satz für ein Ereignis des Wetterdienstes, sonst der Hinweis auf die Einzelheiten."""
    schluessel = f"dwd_{kennung(ereignis)}"
    return schluessel if schluessel in alle() else "warnung_einzelheiten"


def zeitraum(von: datetime | None, bis: datetime | None, jetzt: datetime) -> list[str]:
    """"Ab sofort." oder "Ab 17 Uhr." oder "Ab morgen 6 Uhr.", dazu "Bis ..." (alles in der Zone von jetzt).
    Weiter als morgen bleibt die Angabe weg; die Mitteilung zeigt dann den Titel."""
    teile: list[str] = []
    heute = jetzt.date()

    def tag(t: datetime) -> str | None:
        abstand = (t.date() - heute).days
        return "" if abstand == 0 else "_morgen" if abstand == 1 else None

    if von is not None and von > jetzt:
        t = von.astimezone(jetzt.tzinfo)
        if (vorsilbe := tag(t)) is not None:
            teile.append(f"ab{vorsilbe}_{t.hour}")
    else:
        teile.append("ab_sofort")
    if bis is not None:
        t = bis.astimezone(jetzt.tzinfo)
        if (vorsilbe := tag(t)) is not None:
            teile.append(f"bis{vorsilbe}_{t.hour}")
    return teile
