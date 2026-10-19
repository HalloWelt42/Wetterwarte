"""Buchführung der Meldungen: was aus der Lage neu zu melden ist (Regeln in docs/WARNUNGEN.md).

Reine Funktion `pruefe`: Lage, Gedächtnis des Kanals (je Episodenschlüssel eine Erinnerung), Einstellungen des
Geräts. Heraus kommen die neuen Meldungen und das neue Gedächtnis. Push und Ansage rufen sie mit ihrem eigenen
Gedächtnis auf; die Nachtruhe reicht der Push-Kanal als `zulassen` hinein."""

from collections.abc import Callable
from datetime import datetime, timedelta

from pydantic import BaseModel

from . import ansagen
from .schemas.geraete import Ansage, Meldeeinstellungen
from .schemas.lage import Ereignis, Meldeart, Quelle

ENTWARNUNG_AB_MIN = 10  # nur entwarnen, wenn der angekündigte Beginn noch so weit weg war
NACH_HINTEN_STUFEN = 2  # so viele Vorlaufstufen später, und die Buchführung meldet beim Näherkommen erneut


class Erinnerung(BaseModel):
    """Zuletzt Gemeldetes einer Episode."""

    art: Meldeart
    klasse: str
    rang: int
    stufe: int
    vorlaufstufe: int | None
    beginn: datetime | None
    laeuft: bool
    quelle: Quelle


def gewollt(e: Ereignis, einst: Meldeeinstellungen) -> bool:
    """Will das Gerät dieses Ereignis jetzt hören (Art, Mindeststärke, Vorlauf)?"""
    if e.art not in einst.arten:
        return False
    if e.art == "niederschlag" and e.rang < einst.niederschlag_ab:
        return False
    if e.art == "wind" and e.rang < einst.wind_ab:
        return False
    if e.vorlaufstufe is None:
        # ohne Vorlauf (Blitze) oder ohne Staffel (amtliche Warnungen) sofort; gestaffelte Arten erst ab ihrer
        # größten Vorlaufstufe
        return e.vorlauf_min is None or _stufen(e.art) is None
    return e.vorlaufstufe <= einst.vorlauf_min


def in_ruhe(einst: Meldeeinstellungen, stunde: int) -> bool:
    """Liegt die volle Stunde (Ortszeit) in der Nachtruhe? Über Mitternacht (22 bis 7) wie am Tag (13 bis 15)."""
    n = einst.nachtruhe
    if not n.an or n.von == n.bis:
        return False
    return (stunde >= n.von or stunde < n.bis) if n.von > n.bis else n.von <= stunde < n.bis


def _stufen(art: Meldeart) -> list[int] | None:
    return next((a.get("vorlaufstufen") for a in ansagen.katalog()["arten"] if a["schluessel"] == art), None)


def _stufenindex(art: Meldeart, stufe: int | None) -> int | None:
    stufen = _stufen(art)
    if stufe is None or not stufen or stufe not in stufen:
        return None
    return sorted(stufen, reverse=True).index(stufe)


def _erinnerung(e: Ereignis) -> Erinnerung:
    return Erinnerung(art=e.art, klasse=e.klasse, rang=e.rang, stufe=e.stufe, vorlaufstufe=e.vorlaufstufe,
                      beginn=e.beginn, laeuft=e.laeuft, quelle=e.quelle)


def _ansage(e: Ereignis) -> Ansage:
    return Ansage(art=e.art, schluessel=e.schluessel, stufe=e.stufe, titel=e.titel, text=e.text, bausteine=e.bausteine)


def entwarnung(schluessel: str, alt: Erinnerung) -> Ansage | None:
    """Entwarnung für eine angekündigte Episode, wenn ihre Klasse eine hat (amtliche Warnungen und Blitze nicht)."""
    klasse = next((k for k in ansagen.katalog()["klassen"].get(alt.art, []) if k["schluessel"] == alt.klasse), None)
    if not klasse or "entwarnung" not in klasse:
        return None
    bausteine = [klasse["entwarnung"]]
    return Ansage(art=alt.art, schluessel=schluessel, stufe=alt.stufe, titel=f"Entwarnung: {klasse['name']} bleibt aus",
                  text=ansagen.text(bausteine), bausteine=bausteine, entwarnung=True)


def pruefe(
    lage: list[Ereignis],
    vorher: dict[str, Erinnerung],
    einst: Meldeeinstellungen,
    jetzt: datetime,
    zulassen: Callable[[Ansage], bool] = lambda _: True,
    ausgefallen: frozenset[Quelle] = frozenset(),
) -> tuple[list[Ansage], dict[str, Erinnerung]]:
    """Neue Meldungen und neues Gedächtnis. Eine Meldung, die `zulassen` ablehnt (Nachtruhe), verändert das
    Gedächtnis nicht. Erinnerungen, deren Quelle gerade ausgefallen ist, bleiben unverändert stehen: ein
    Ausfall ist kein Ende der Lage und darf weder entwarnen noch beim Zurückkehren erneut melden."""
    meldungen: list[Ansage] = []
    gedaechtnis: dict[str, Erinnerung] = {}

    for e in lage:
        alt = vorher.get(e.schluessel)
        if e.laeuft:
            gedaechtnis[e.schluessel] = _erinnerung(e)
            continue
        if alt is not None and alt.laeuft:
            alt = None  # die vorige Episode ist vorbei, diese ist neu
        if not gewollt(e, einst):
            if alt is not None:
                gedaechtnis[e.schluessel] = alt
            continue
        dringlicher = alt is not None and e.vorlaufstufe is not None and alt.vorlaufstufe is not None and e.vorlaufstufe < alt.vorlaufstufe
        if alt is None or e.rang > alt.rang or dringlicher:
            meldung = _ansage(e)
            if zulassen(meldung):
                meldungen.append(meldung)
                gedaechtnis[e.schluessel] = _erinnerung(e)
            elif alt is not None:
                gedaechtnis[e.schluessel] = alt
            continue
        neu = alt.model_copy(update={"beginn": e.beginn})
        a, n = _stufenindex(e.art, alt.vorlaufstufe), _stufenindex(e.art, e.vorlaufstufe)
        if a is not None and n is not None and a - n >= NACH_HINTEN_STUFEN:
            neu = neu.model_copy(update={"vorlaufstufe": e.vorlaufstufe})  # Beginn deutlich später: still neu scharf
        gedaechtnis[e.schluessel] = neu

    for schluessel, alt in vorher.items():
        if schluessel in gedaechtnis:
            continue
        if alt.quelle in ausgefallen:
            gedaechtnis[schluessel] = alt
            continue
        if alt.laeuft or alt.beginn is None or alt.beginn <= jetzt + timedelta(minutes=ENTWARNUNG_AB_MIN):
            continue  # eingetreten oder ohnehin vorbei: still vergessen
        if (meldung := entwarnung(schluessel, alt)) is None:
            continue
        if zulassen(meldung):
            meldungen.append(meldung)
        else:
            gedaechtnis[schluessel] = alt  # nach der Nachtruhe noch einmal prüfen
    return meldungen, gedaechtnis
