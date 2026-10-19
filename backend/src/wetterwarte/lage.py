"""Lage am Ort: welche Wetterereignisse kommen oder laufen (Regeln in docs/WARNUNGEN.md).

Reine Funktionen ohne Abrufe: sie bekommen die Rohwerte der Bereiche (Vorhersage, Radar-Nowcast, Warnungen,
Blitze) und `jetzt`. Was gemeldet wird, entscheidet danach melden.py; hier steht nur, was ist. Schwellen,
Klassen und Vorlaufstufen kommen aus gemeinsam/meldungen.json."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from . import ansagen
from .schemas.lage import Ereignis, Meldeart, Quelle
from .zeit import lokal, zone

NASS_AB = 0.2  # mm/h, darunter gilt ein Schritt als trocken
EPISODE_MIN = 15  # so lange muss es am Stück nass sein, damit eine Episode zählt
STAERKE_FENSTER_MIN = 60  # die Stärke einer Episode bemisst sich an ihrer ersten Stunde
SCHNEE_CODES = {71, 73, 75, 77, 85, 86}
GEFRIEREND_CODES = {56, 57, 66, 67}


@dataclass(frozen=True)
class Schritt:
    """Ein Abschnitt des Niederschlagsverlaufs: Beginn, Dauer, Rate in mm/h, Quelle."""

    beginn: datetime
    dauer_min: int
    rate: float
    quelle: Quelle

    @property
    def ende(self) -> datetime:
        return self.beginn + timedelta(minutes=self.dauer_min)


def _art(art: Meldeart) -> dict:
    return next(a for a in ansagen.katalog()["arten"] if a["schluessel"] == art)


def vorlaufstufe(art: Meldeart, minuten: int) -> int | None:
    """Kleinste Vorlaufstufe der Art, die den Vorlauf noch abdeckt; None, wenn er über der größten liegt."""
    passend = [s for s in _art(art)["vorlaufstufen"] if minuten <= s]
    return min(passend) if passend else None


def _zahl(wert: object) -> float | None:
    return float(wert) if isinstance(wert, int | float) else None


# --- Niederschlag --------------------------------------------------------------------------------------------


def niederschlagsverlauf(basis: dict | None, nowcast: dict | None, tz: str, jetzt: datetime, horizont_min: int) -> list[Schritt]:
    """Rate je Abschnitt von jetzt bis zum Horizont: Radar-Nowcast (5 min), danach Viertelstunden des Modells,
    danach Stunden. Später beginnende Quellen setzen dort ein, wo die genauere endet."""
    ende = jetzt + timedelta(minutes=horizont_min)
    schritte: list[Schritt] = []

    def anhaengen(beginn: datetime, dauer_min: int, rate: float | None, quelle: Quelle) -> None:
        schluss = beginn + timedelta(minutes=dauer_min)
        ab = max(beginn, jetzt, schritte[-1].ende if schritte else jetzt)
        if rate is None or schluss <= ab or ab >= ende:
            return
        schritte.append(Schritt(ab, max(1, round((min(schluss, ende) - ab).total_seconds() / 60)), rate, quelle))

    if nowcast:
        start = datetime.fromisoformat(nowcast["basis"])
        for versatz, rate in zip(nowcast["versatz_min"], nowcast["werte"], strict=False):
            if rate is None:
                break  # Lücke im Radar: ab hier zählt das Modell
            anhaengen(start + timedelta(minutes=versatz), 5, rate, "radar")
    if basis:
        viertel = basis.get("minutely_15") or {}
        for t, mm in zip(viertel.get("time") or [], viertel.get("precipitation") or [], strict=False):
            wert = _zahl(mm)
            anhaengen(lokal(t, tz), 15, wert * 4 if wert is not None else None, "vorhersage")
        stunden = basis.get("hourly") or {}
        for t, mm in zip(stunden.get("time") or [], stunden.get("precipitation") or [], strict=False):
            anhaengen(lokal(t, tz), 60, _zahl(mm), "vorhersage")
    return schritte


def _code_um(basis: dict | None, tz: str, zeitpunkt: datetime) -> int | None:
    stunden = (basis or {}).get("hourly") or {}
    for t, code in zip(stunden.get("time") or [], stunden.get("weather_code") or [], strict=False):
        beginn = lokal(t, tz)
        if beginn <= zeitpunkt < beginn + timedelta(hours=1):
            return int(code) if isinstance(code, int | float) else None
    return None


def _niederschlag_klasse(rate: float, code: int | None) -> dict:
    klassen = ansagen.katalog()["klassen"]["niederschlag"]
    if code in GEFRIEREND_CODES:
        return next(k for k in klassen if k.get("glatteis"))
    schnee = code in SCHNEE_CODES
    passend = [k for k in klassen if bool(k.get("schnee")) == schnee and not k.get("glatteis") and rate >= k["ab"]]
    return max(passend, key=lambda k: k["rang"]) if passend else min(
        (k for k in klassen if bool(k.get("schnee")) == schnee and not k.get("glatteis")), key=lambda k: k["rang"]
    )


def _niederschlag_stufe(klasse: dict, rate: float) -> int:
    if "stufe" in klasse:
        return int(klasse["stufe"])
    return max(s["stufe"] for s in ansagen.katalog()["niederschlag_stufen"] if rate >= s["ab"])


def niederschlag(schritte: list[Schritt], basis: dict | None, tz: str, jetzt: datetime) -> Ereignis | None:
    """Nächste Niederschlagsepisode: mindestens 15 Minuten am Stück nass. Regnet es schon, läuft sie."""
    i = 0
    while i < len(schritte):
        if schritte[i].rate < NASS_AB:
            i += 1
            continue
        j = i
        while j < len(schritte) and schritte[j].rate >= NASS_AB:
            j += 1
        episode = schritte[i:j]
        if (episode[-1].ende - episode[0].beginn) >= timedelta(minutes=EPISODE_MIN):
            return _niederschlag_ereignis(episode, basis, tz, jetzt)
        i = j
    return None


def _niederschlag_ereignis(episode: list[Schritt], basis: dict | None, tz: str, jetzt: datetime) -> Ereignis:
    beginn = episode[0].beginn
    fenster = beginn + timedelta(minutes=STAERKE_FENSTER_MIN)
    rate = max(s.rate for s in episode if s.beginn < fenster)
    klasse = _niederschlag_klasse(rate, _code_um(basis, tz, beginn))
    stufe = _niederschlag_stufe(klasse, rate)
    laeuft = beginn <= jetzt + timedelta(minutes=1)
    return _angekuendigt("niederschlag", "niederschlag", klasse, stufe, beginn, laeuft, episode[0].quelle, jetzt)


def _angekuendigt(art: Meldeart, schluessel: str, klasse: dict, stufe: int, beginn: datetime, laeuft: bool,
                  quelle: Quelle, jetzt: datetime, zusatz: list[str] | None = None) -> Ereignis:
    """Ereignis mit Vorlauf: Kernsatz "Es wird in deiner Region in ... ", davor "Achtung." ab Stufe 3."""
    if laeuft:
        return Ereignis(art=art, schluessel=schluessel, klasse=klasse["schluessel"], rang=klasse["rang"], stufe=stufe,
                        beginn=beginn, laeuft=True, quelle=quelle, titel=f"{klasse['name']} jetzt", text="", bausteine=[])
    minuten = max(0, round((beginn - jetzt).total_seconds() / 60))
    bausteine = (["achtung"] if stufe >= 3 else []) + [ansagen.kernsatz(klasse["schluessel"], minuten)] + (zusatz or [])
    return Ereignis(
        art=art,
        schluessel=schluessel,
        klasse=klasse["schluessel"],
        rang=klasse["rang"],
        stufe=stufe,
        beginn=beginn,
        vorlauf_min=minuten,
        vorlaufstufe=vorlaufstufe(art, minuten),
        quelle=quelle,
        titel=f"{klasse['name']} {ansagen.zeit(minuten)['text']}",
        text=ansagen.text(bausteine),
        bausteine=bausteine,
    )


# --- Gewitter und Wind aus den Stunden des Modells -----------------------------------------------------------


def _stunden(basis: dict | None, tz: str, jetzt: datetime, horizont_min: int, feld: str) -> list[tuple[datetime, float]]:
    """(Beginn, Wert) der Stunden, die nach jetzt enden und vor dem Horizont beginnen."""
    stunden = (basis or {}).get("hourly") or {}
    ende = jetzt + timedelta(minutes=horizont_min)
    werte = []
    for t, w in zip(stunden.get("time") or [], stunden.get(feld) or [], strict=False):
        beginn, wert = lokal(t, tz), _zahl(w)
        if wert is not None and beginn + timedelta(hours=1) > jetzt and beginn < ende:
            werte.append((beginn, wert))
    return werte


def gewitter(basis: dict | None, tz: str, jetzt: datetime) -> Ereignis | None:
    """Erste vorhergesagte Gewitterstunde; die Klasse nach dem stärksten Code der zusammenhängenden Stunden."""
    klassen = ansagen.katalog()["klassen"]["gewitter"]
    stunden = _stunden(basis, tz, jetzt, _art("gewitter")["horizont_min"], "weather_code")

    def klasse_von(code: float) -> dict | None:
        return next((k for k in klassen if int(code) in k["codes"]), None)

    for i, (beginn, code) in enumerate(stunden):
        if klasse_von(code) is None:
            continue
        folge = []
        for _, c in stunden[i:]:
            if (k := klasse_von(c)) is None:
                break
            folge.append(k)
        klasse = max(folge, key=lambda k: k["rang"])
        # Eine Gewitterstunde, die schon begonnen hat, wird noch angekündigt (das Modell sagt "jetzt möglich").
        return _angekuendigt("gewitter", "gewitter", klasse, klasse["stufe"], max(beginn, jetzt), False, "vorhersage", jetzt)
    return None


def wind(basis: dict | None, tz: str, jetzt: datetime) -> Ereignis | None:
    """Erste Episode mit Böen ab der kleinsten Klasse; angekündigt wird die stärkste Klasse der Episode zu ihrem
    ersten Auftreten, dazu die Spitzenböe."""
    klassen = ansagen.katalog()["klassen"]["wind"]
    schwelle = min(k["ab"] for k in klassen)
    stunden = _stunden(basis, tz, jetzt, _art("wind")["horizont_min"], "wind_gusts_10m")
    start = next((i for i, (_, b) in enumerate(stunden) if b >= schwelle), None)
    if start is None:
        return None
    episode = []
    for beginn, b in stunden[start:]:
        if b < schwelle:
            break
        episode.append((beginn, b))
    spitze = max(b for _, b in episode)
    klasse = max((k for k in klassen if spitze >= k["ab"]), key=lambda k: k["rang"])
    beginn = max(next(t for t, b in episode if b >= klasse["ab"]), jetzt)
    laeuft = beginn <= jetzt
    return _angekuendigt("wind", "wind", klasse, klasse["stufe"], beginn, laeuft, "vorhersage", jetzt, [ansagen.boeen(spitze)])


# --- Blitze und amtliche Warnungen ---------------------------------------------------------------------------


def blitze(roh: dict | None, jetzt: datetime) -> Ereignis | None:
    """Nächster Einschlag der letzten Minuten im Umkreis: je näher, desto höher der Rang."""
    regel = ansagen.katalog()["blitze"]
    weiteste = max(e["bis_km"] for e in regel["entfernungen"])
    grenze_ms = (jetzt - timedelta(minutes=regel["fenster_min"])).timestamp() * 1000
    nah = [e for e in (roh or {}).get("einschlaege") or [] if e["zeit"] >= grenze_ms and e["km"] <= weiteste]
    if not nah:
        return None
    km = min(e["km"] for e in nah)
    stufe_ = min((e for e in regel["entfernungen"] if km <= e["bis_km"]), key=lambda e: e["bis_km"])
    bausteine = (["achtung"] if stufe_["stufe"] >= 3 else []) + [ansagen.blitze(km)]
    return Ereignis(
        art="gewitter",
        schluessel="blitze",
        klasse=f"blitze_{stufe_['bis_km']}",
        rang=stufe_["rang"],
        stufe=stufe_["stufe"],
        beginn=None,
        quelle="blitze",
        titel=f"Gewitter in {max(1, round(km))} Kilometern Entfernung",
        text=ansagen.text(bausteine),
        bausteine=bausteine,
    )


def warnungen(liste: list[dict] | None, jetzt: datetime) -> list[Ereignis]:
    """Jede amtliche Warnung ein Ereignis; gemeldet wird sie einmal, wenn sie erscheint."""
    ergebnis = []
    for w in liste or []:
        von = datetime.fromisoformat(w["von"]) if w.get("von") else None
        bis = datetime.fromisoformat(w["bis"]) if w.get("bis") else None
        if bis is not None and bis <= jetzt:
            continue
        stufe = max(1, min(4, int(w.get("stufe") or 1)))
        bausteine = [f"warnung_{stufe}", ansagen.dwd(w["ereignis"]), *ansagen.zeitraum(von, bis, jetzt)]
        ergebnis.append(
            Ereignis(
                art="warnung",
                schluessel=f"warnung:{ansagen.kennung(w['ereignis'])}:{von.isoformat() if von else ''}",
                klasse=w["ereignis"],
                rang=stufe,
                stufe=stufe,
                beginn=von,
                vorlauf_min=max(0, round((von - jetzt).total_seconds() / 60)) if von else None,
                quelle="amtlich",
                titel=f"Warnung Stufe {stufe}: {w['ereignis']}",
                text=ansagen.text(bausteine),
                bausteine=bausteine,
            )
        )
    return ergebnis


def ermittle(basis: dict | None, nowcast: dict | None, warnliste: list[dict] | None, blitze_roh: dict | None,
             tz: str, jetzt: datetime) -> list[Ereignis]:
    """Alle Ereignisse am Ort, höchste Stufe zuerst. Heute und morgen gelten in der Zeitzone des Orts."""
    jetzt = jetzt.astimezone(zone(tz))
    schritte = niederschlagsverlauf(basis, nowcast, tz, jetzt, _art("niederschlag")["horizont_min"])
    kandidaten = [
        niederschlag(schritte, basis, tz, jetzt),
        gewitter(basis, tz, jetzt),
        blitze(blitze_roh, jetzt),
        wind(basis, tz, jetzt),
    ]
    ereignisse = warnungen(warnliste, jetzt) + [e for e in kandidaten if e is not None]
    return sorted(ereignisse, key=lambda e: (-e.stufe, e.vorlauf_min if e.vorlauf_min is not None else -1))
