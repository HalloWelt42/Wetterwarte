"""Web Push von Ende zu Ende gegen einen lokalen Push-Dienst: VAPID-Anspruch, Kopfzeilen und die verschlüsselte
Nutzlast, entschlüsselt mit den Schlüsseln des Abos wie im Browser."""

import base64
import json
import os

import http_ece
from aiohttp import web
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from py_vapid import Vapid02
from py_vapid.jwt import decode

from wetterwarte import push
from wetterwarte.config import settings


def _b64(daten: bytes) -> str:
    return base64.urlsafe_b64encode(daten).rstrip(b"=").decode()


async def _dienst(antwort_status: int):
    """Lokaler Push-Dienst: nimmt eine Mitteilung an und merkt sich Kopf und Körper."""
    empfangen: dict = {}

    async def annehmen(anfrage: web.Request) -> web.Response:
        empfangen["kopf"] = dict(anfrage.headers)
        empfangen["koerper"] = await anfrage.read()
        return web.Response(status=antwort_status)

    app = web.Application()
    app.router.add_post("/abo/{kennung}", annehmen)
    lauf = web.AppRunner(app)
    await lauf.setup()
    stelle = web.TCPSite(lauf, "127.0.0.1", 0)
    await stelle.start()
    port = stelle._server.sockets[0].getsockname()[1]  # type: ignore[union-attr]
    return lauf, f"http://127.0.0.1:{port}/abo/geraet-1", empfangen


async def test_mitteilung_kommt_verschluesselt_und_unterschrieben_an(monkeypatch):
    schluessel = Vapid02()
    schluessel.generate_keys()
    monkeypatch.setattr(push, "_vapid", schluessel)
    # Schlüssel des Abos, wie der Browser sie erzeugt
    privat = ec.generate_private_key(ec.SECP256R1())
    p256dh = privat.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    auth = os.urandom(16)

    lauf, endpunkt, empfangen = await _dienst(201)
    try:
        nutzlast = {"titel": "Köln: Leichter Regen in 30 Minuten", "text": "Es wird in deiner Region in 30 Minuten leicht regnen.",
                    "tag": "koeln:niederschlag", "url": "/telefon?ort=koeln&blatt=lage", "stufe": 1}
        assert await push.sende(endpunkt, _b64(p256dh), _b64(auth), nutzlast, ttl=1200, dringend=False) == "ok"
    finally:
        await lauf.cleanup()

    kopf = {k.lower(): v for k, v in empfangen["kopf"].items()}
    assert kopf["ttl"] == "1200" and kopf["urgency"] == "normal" and kopf["content-encoding"] == "aes128gcm"
    assert kopf["topic"] == push.thema("koeln:niederschlag") and len(kopf["topic"]) <= 32
    # VAPID: Token mit dem öffentlichen Schlüssel des Servers prüfbar, Anspruch für genau diesen Push-Dienst
    teile = dict(t.strip().split("=", 1) for t in kopf["authorization"].removeprefix("vapid ").split(","))
    anspruch = decode(teile["t"], teile["k"])
    assert teile["k"] == await push.oeffentlich()
    assert anspruch["sub"] == settings.push_kontakt and anspruch["aud"] == endpunkt.split("/abo")[0]
    # Nutzlast entschlüsseln wie der Browser
    klartext = http_ece.decrypt(empfangen["koerper"], private_key=privat, auth_secret=auth, version="aes128gcm")
    assert json.loads(klartext) == nutzlast


async def test_erloschenes_abo_meldet_weg(monkeypatch):
    schluessel = Vapid02()
    schluessel.generate_keys()
    monkeypatch.setattr(push, "_vapid", schluessel)
    privat = ec.generate_private_key(ec.SECP256R1())
    p256dh = privat.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    lauf, endpunkt, _ = await _dienst(410)
    try:
        assert await push.sende(endpunkt, _b64(p256dh), _b64(os.urandom(16)), {"tag": "x"}, ttl=60, dringend=True) == "weg"
    finally:
        await lauf.cleanup()
