"""Bereiche: frisch, alt bei Ausfall, fehlt ohne Stand; Sperre nach Fehlschlag."""

import pytest

from wetterwarte import bereiche, cache
from wetterwarte.bereiche import Regel


@pytest.fixture
def speicher(monkeypatch):
    daten: dict = {}

    async def hole(k):
        return daten.get(k)

    async def setze(k, w, ttl):
        daten[k] = w

    monkeypatch.setattr(cache, "hole", hole)
    monkeypatch.setattr(cache, "setze", setze)
    bereiche._fehlschlag.clear()
    return daten


async def _kaputt():
    raise RuntimeError("Quelle tot")


async def test_ok_dann_alt_dann_fehlt(speicher, monkeypatch):
    async def gut():
        return {"a": 1}

    regel = Regel(frisch=0, haltbar=3600)
    e = await bereiche.lade("t:1", regel, gut)
    assert e.status == "ok" and e.wert == {"a": 1}
    e = await bereiche.lade("t:1", regel, _kaputt)
    assert e.status == "alt" and e.wert == {"a": 1} and e.stand is not None
    e = await bereiche.lade("t:2", regel, _kaputt)
    assert e.status == "fehlt" and e.wert is None


async def test_sperre_nach_fehlschlag(speicher):
    aufrufe = 0

    async def zaehle():
        nonlocal aufrufe
        aufrufe += 1
        raise RuntimeError("tot")

    regel = Regel(frisch=0, haltbar=60)
    await bereiche.lade("t:3", regel, zaehle)
    await bereiche.lade("t:3", regel, zaehle)
    assert aufrufe == 1
