"""Telefon-Layouts: Katalog, Vorlage und Prüfung.

Der Katalog (gemeinsam/telefon-katalog.json) ist die einzige Wahrheit über
die Telefon-Kacheltypen, ihre erlaubten Größen und Einstellungen. Die Oberfläche baut ihn beim
Bau ein, das Backend liest ihn hier und prüft jedes gespeicherte Layout dagegen."""

import uuid

from pydantic import BaseModel, Field

from .gemeinsam import telefon_katalog


class TelefonKachel(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    typ: str
    x: int
    y: int
    w: int
    h: int
    conf: dict = Field(default_factory=dict)


class TelefonLayout(BaseModel):
    """Seiten der Telefonansicht mit ihren Kacheln (Schlüssel aus katalog()["seiten"])."""

    seiten: dict[str, list[TelefonKachel]] = Field(default_factory=dict)


def katalog() -> dict:
    return telefon_katalog()


def neue_id(typ: str) -> str:
    return f"{typ}-{uuid.uuid4()}"


def vorlage(profilname: str = "") -> TelefonLayout:
    """Vorlage für ein Profil, mit frischen Kachel-IDs. Für die Standardprofile (Unwetter, Garten,
    Reise) gibt es eigene Seiten im Katalog; fehlt eine Seite dort, gilt die allgemeine Vorlage."""
    seiten = {**katalog()["vorlage"], **katalog().get("profilvorlagen", {}).get(profilname, {})}
    return TelefonLayout(seiten={seite: [TelefonKachel(id=neue_id(k["typ"]), **k) for k in kacheln] for seite, kacheln in seiten.items()})


def _pruefe_conf(typ: str, conf: dict) -> None:
    einstellungen = {e["schluessel"]: e for e in katalog()["typen"][typ]["einstellungen"]}
    for schluessel, wert in conf.items():
        e = einstellungen.get(schluessel)
        if e is None:
            raise ValueError(f"{typ}: unbekannte Einstellung {schluessel}")
        erlaubt = {o["wert"] for o in e["optionen"]}
        if e["art"] == "auswahl" and wert not in erlaubt:
            raise ValueError(f"{typ}: {schluessel} = {wert} ist nicht vorgesehen")
        if e["art"] == "mehrfach" and (not isinstance(wert, list) or not set(wert) <= erlaubt):
            raise ValueError(f"{typ}: {schluessel} enthält nicht vorgesehene Werte")


def pruefe(layout: TelefonLayout) -> None:
    """Je Seite: Typ (und ob er auf diese Seite darf), Größe, Lage und Einstellungen jeder Kachel
    gegen den Katalog; keine Überlappung; jede Kachel-ID nur einmal im ganzen Layout.
    Wirft ValueError mit lesbarem Grund."""
    typen = katalog()["typen"]
    spalten = katalog()["spalten"]
    seiten = {s["schluessel"] for s in katalog()["seiten"]}
    ids: set[str] = set()
    for seite, kacheln in layout.seiten.items():
        if seite not in seiten:
            raise ValueError(f"Unbekannte Seite {seite}")
        if len(kacheln) > 60:
            raise ValueError(f"Seite {seite} hat zu viele Kacheln")
        belegt: dict[tuple[int, int], str] = {}
        for k in kacheln:
            if k.typ not in typen:
                raise ValueError(f"Unbekannter Kacheltyp {k.typ}")
            if seite not in typen[k.typ]["seiten"]:
                raise ValueError(f"{k.typ} gehört nicht auf die Seite {seite}")
            if f"{k.w}x{k.h}" not in typen[k.typ]["groessen"]:
                raise ValueError(f"{k.typ}: Größe {k.w}x{k.h} ist nicht vorgesehen")
            if k.x < 0 or k.y < 0 or k.x + k.w > spalten or k.y > 200:
                raise ValueError(f"{k.typ}: Lage {k.x}, {k.y} liegt außerhalb des Rasters")
            if k.id in ids:
                raise ValueError(f"Kachel-ID {k.id} kommt doppelt vor")
            ids.add(k.id)
            _pruefe_conf(k.typ, k.conf)
            for dx in range(k.w):
                for dy in range(k.h):
                    feld = (k.x + dx, k.y + dy)
                    if feld in belegt:
                        raise ValueError(f"{k.typ} überlappt {belegt[feld]} bei {feld[0]}, {feld[1]}")
                    belegt[feld] = k.typ
