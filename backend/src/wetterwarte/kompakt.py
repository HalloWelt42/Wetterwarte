"""Telefon-Antwort aus den Datenbereichen eines Orts (siehe schemas/kompakt.py).

`baue` ist eine reine Funktion ohne Abrufe: Sie bekommt die Rohwerte der Bereiche und formt
sie um. `lade` holt die Bereiche über den Wetterdienst und ruft `baue` auf."""

import asyncio
from datetime import date, datetime

from . import wetterdienst
from .bereiche import Ergebnis
from .models.ort import Ort
from .providers.openmeteo import jetzt_index, viertel_index
from .schemas.kompakt import (
    Bereich,
    Blitze,
    Einschlag,
    Jetzt,
    Kompakt,
    KOrt,
    Luft,
    Pollen,
    Pollenart,
    Regen,
    Schadstoff,
    Stunde,
    Tag,
    Warnung,
)
from .zeit import jetzt, lokal, zone

ZURUECK_H = 6
VORAUS_H = 48
REGEN_SCHRITTE = 8  # 2 Stunden in Viertelstunden
REGEN_SCHWELLE = 0.2  # mm/h, darunter gilt es als trocken

_SCHADSTOFFE = (
    ("pm2_5", "Feinstaub PM2,5", "µg/m³"),
    ("pm10", "Feinstaub PM10", "µg/m³"),
    ("o3", "Ozon", "µg/m³"),
    ("no2", "Stickstoffdioxid", "µg/m³"),
)


def _zahl(wert: object, ersatz: float = 0.0) -> float:
    return float(wert) if isinstance(wert, int | float) else ersatz


def _jetzt(roh: dict, tz: str, h: dict, idx: int) -> Jetzt:
    c = roh["current"]
    druck = h.get("pressure_msl") or []
    tendenz = None
    if idx >= 3 and len(druck) > idx and druck[idx] is not None and druck[idx - 3] is not None:
        tendenz = float(druck[idx]) - float(druck[idx - 3])
    sicht = (h.get("visibility") or [None] * (idx + 1))[idx]
    return Jetzt(
        zeit=lokal(c["time"], tz),
        temp=_zahl(c["temperature_2m"]),
        gefuehlt=_zahl(c["apparent_temperature"]),
        code=int(c["weather_code"]),
        tag=bool(c["is_day"]),
        feuchte=_zahl(c["relative_humidity_2m"]),
        taupunkt=_zahl(c["dew_point_2m"]),
        druck=_zahl(c["pressure_msl"]),
        druck_tendenz=tendenz,
        sicht_km=sicht / 1000 if isinstance(sicht, int | float) else None,
        bewoelkung=_zahl(c["cloud_cover"]),
        wind=_zahl(c["wind_speed_10m"]),
        boeen=_zahl(c.get("wind_gusts_10m")),
        wind_grad=_zahl(c["wind_direction_10m"]),
        uv=_zahl(c.get("uv_index")),
        regen_mm=_zahl(c.get("precipitation")),
    )


def _stunden(h: dict, tz: str, idx: int) -> tuple[list[Stunde], int]:
    von = max(0, idx - ZURUECK_H)
    bis = min(len(h["time"]), idx + VORAUS_H + 1)

    def feld(name: str, i: int) -> object:
        werte = h.get(name) or []
        return werte[i] if i < len(werte) else None

    stunden = []
    for i in range(von, bis):
        sicht = feld("visibility", i)
        stunden.append(
            Stunde(
                zeit=lokal(h["time"][i], tz),
                temp=_zahl(feld("temperature_2m", i)),
                gefuehlt=_zahl(feld("apparent_temperature", i)),
                code=int(_zahl(feld("weather_code", i))),
                tag=bool(feld("is_day", i)),
                regen_wahrsch=feld("precipitation_probability", i),
                regen_mm=_zahl(feld("precipitation", i)),
                wind=_zahl(feld("wind_speed_10m", i)),
                boeen=_zahl(feld("wind_gusts_10m", i)),
                wind_grad=_zahl(feld("wind_direction_10m", i)),
                uv=_zahl(feld("uv_index", i)),
                feuchte=_zahl(feld("relative_humidity_2m", i)),
                taupunkt=_zahl(feld("dew_point_2m", i)),
                druck=_zahl(feld("pressure_msl", i)),
                sicht_km=sicht / 1000 if isinstance(sicht, int | float) else None,
                bewoelkung=_zahl(feld("cloud_cover", i)),
            )
        )
    return stunden, idx - von


def _uv_spitzen(h: dict) -> dict[str, str]:
    """Je Datum (Ortszeit) die Stunde mit dem höchsten UV-Wert, soweit Stundenwerte vorliegen."""
    spitzen: dict[str, tuple[float, str]] = {}
    for t, uv in zip(h.get("time") or [], h.get("uv_index") or [], strict=False):
        if isinstance(uv, int | float) and (t[:10] not in spitzen or uv > spitzen[t[:10]][0]):
            spitzen[t[:10]] = (float(uv), t)
    return {datum: t for datum, (uv, t) in spitzen.items() if uv > 0}


def _tage(d: dict, tz: str, h: dict) -> list[Tag]:
    spitzen = _uv_spitzen(h)
    tage = []
    for i, datum in enumerate(d["time"]):

        def feld(name: str) -> object:
            werte = d.get(name) or []
            return werte[i] if i < len(werte) else None

        auf, unter = feld("sunrise"), feld("sunset")
        tage.append(
            Tag(
                datum=date.fromisoformat(datum),
                code=int(_zahl(feld("weather_code"))),
                hoch=_zahl(feld("temperature_2m_max")),
                tief=_zahl(feld("temperature_2m_min")),
                regen_wahrsch=feld("precipitation_probability_max"),
                regen_mm=_zahl(feld("precipitation_sum")),
                wind_max=_zahl(feld("wind_speed_10m_max")),
                boeen_max=_zahl(feld("wind_gusts_10m_max")),
                uv_max=_zahl(feld("uv_index_max")),
                uv_max_zeit=lokal(spitzen[datum], tz) if datum in spitzen else None,
                sonnenaufgang=lokal(auf, tz) if isinstance(auf, str) else None,
                sonnenuntergang=lokal(unter, tz) if isinstance(unter, str) else None,
                tageslaenge_s=_zahl(feld("daylight_duration")),
            )
        )
    return tage


def _regen(roh: dict) -> Regen | None:
    mm = roh.get("minutely_15") or {}
    if not mm.get("time"):
        return None
    i = viertel_index(mm["time"], roh["current"]["time"])
    werte = [_zahl(w) * 4 for w in mm["precipitation"][i : i + REGEN_SCHRITTE]]  # mm je 15 min -> mm/h
    nass = [w >= REGEN_SCHWELLE for w in werte]
    beginn = nass.index(True) if True in nass else None
    ende = None
    if beginn is not None and False in nass[beginn:]:
        ende = beginn + nass[beginn:].index(False)
    return Regen(
        werte=[round(w, 2) for w in werte],
        beginn_min=beginn * 15 if beginn is not None else None,
        ende_min=ende * 15 if ende is not None else None,
        max_mm_h=round(max(werte, default=0.0), 2),
    )


def _blitze(roh: dict) -> Blitze:
    jetzt_ms = jetzt().timestamp() * 1000
    alle = roh.get("einschlaege") or []
    letzte_30 = [e for e in alle if jetzt_ms - e["zeit"] <= 30 * 60_000]
    naechster = min(letzte_30, key=lambda e: e["km"], default=None)
    return Blitze(
        anzahl_30=len(letzte_30),
        anzahl_60=int(roh.get("anzahl") or len(alle)),
        naechster_km=naechster["km"] if naechster else None,
        naechster_grad=naechster["grad"] if naechster else None,
        zuletzt=datetime.fromtimestamp(alle[0]["zeit"] / 1000, tz=jetzt().tzinfo) if alle else None,
        einschlaege=[
            Einschlag(km=e["km"], grad=e["grad"], zeit=datetime.fromtimestamp(e["zeit"] / 1000, tz=jetzt().tzinfo))
            for e in letzte_30[:200]
        ],
    )


def _luft(roh: dict) -> Luft:
    return Luft(
        index=int(_zahl(roh.get("aqi"))),
        stufe=str(roh.get("label") or ""),
        schadstoffe=[
            Schadstoff(schluessel=k, titel=t, wert=_zahl(roh.get(k)), einheit=e)
            for k, t, e in _SCHADSTOFFE
            if isinstance(roh.get(k), int | float)
        ],
    )


def _pollen(roh: dict) -> Pollen:
    region = roh.get("region") or {}
    return Pollen(
        region=region.get("partregion_name") or region.get("name") or "",
        arten=[
            Pollenart(
                schluessel=schluessel,
                titel=a["name"],
                heute=_zahl(a["today"]["value"], -1),
                morgen=_zahl(a["tomorrow"]["value"], -1),
                uebermorgen=_zahl(a["dayafter"]["value"], -1),
            )
            for schluessel, a in (roh.get("arten") or {}).items()
        ],
    )


def baue(
    o: Ort,
    basis: Ergebnis[dict],
    warnungen: Ergebnis[list],
    blitze: Ergebnis[dict],
    luft: Ergebnis[dict],
    pollen: Ergebnis[dict],
) -> Kompakt:
    tz = zone(o.zeitzone).key
    roh = basis.wert
    jetzt_wert, stunden, idx, tage, regen = None, [], 0, [], None
    if roh:
        h = roh["hourly"]
        i = jetzt_index(h["time"], roh["current"]["time"])
        jetzt_wert = _jetzt(roh, tz, h, i)
        stunden, idx = _stunden(h, tz, i)
        tage = _tage(roh["daily"], tz, h)
        regen = _regen(roh)
    return Kompakt(
        ort=KOrt(slug=o.slug, name=o.name, region=o.region, lat=o.lat, lon=o.lon, zeitzone=tz),
        zeit=jetzt(),
        bereiche={
            name: Bereich(status=e.status, stand=e.stand)
            for name, e in (("basis", basis), ("warnungen", warnungen), ("blitze", blitze), ("luft", luft), ("pollen", pollen))
        },
        jetzt=jetzt_wert,
        stunden=stunden,
        jetzt_index=idx,
        tage=tage,
        regen=regen,
        # None bei Status ok: der Ort liegt außerhalb des Warngebiets; bei Status fehlt: Quelle ausgefallen
        warnungen=[Warnung(**w) for w in warnungen.wert] if warnungen.wert is not None else None,
        blitze=_blitze(blitze.wert) if blitze.wert else None,
        luft=_luft(luft.wert) if luft.wert else None,
        pollen=_pollen(pollen.wert) if pollen.wert else None,
    )


async def lade(o: Ort) -> Kompakt:
    basis, warnungen, blitze, luft, pollen = await asyncio.gather(
        wetterdienst.basis(o), wetterdienst.warnungen(o), wetterdienst.blitze(o), wetterdienst.luft(o), wetterdienst.pollen(o)
    )
    return baue(o, basis, warnungen, blitze, luft, pollen)
