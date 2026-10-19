"""Web Push: VAPID-Schlüssel und Versand an ein Abo (docs/WARNUNGEN.md).

Der private Schlüssel entsteht beim ersten Bedarf und liegt in der Tabelle einstellung; der öffentliche geht an
die Oberfläche, die damit das Abo beim Browser anlegt. Wechselt der Schlüssel, gelten alte Abos nicht mehr."""

import asyncio
import base64
import hashlib
import json
import logging
from typing import Literal

from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid02
from pywebpush import WebPushException, webpush_async

from .config import settings
from .db import SessionLocal
from .models.einstellung import Einstellung

log = logging.getLogger(__name__)

PRIVAT = "push.vapid.privat"
_vapid: Vapid02 | None = None
_sperre = asyncio.Lock()

Versand = Literal["ok", "weg", "fehler"]


async def vapid() -> Vapid02:
    global _vapid
    if _vapid is not None:
        return _vapid
    async with _sperre:
        if _vapid is None:
            async with SessionLocal() as session:
                zeile = await session.get(Einstellung, PRIVAT)
                if zeile is None:
                    neu = Vapid02()
                    neu.generate_keys()
                    zeile = Einstellung(schluessel=PRIVAT, wert=neu.private_pem().decode())
                    session.add(zeile)
                    await session.commit()
                    log.info("Neuer VAPID-Schlüssel für Web Push angelegt")
                _vapid = Vapid02.from_pem(zeile.wert.encode())
    return _vapid


async def oeffentlich() -> str:
    """Öffentlicher Schlüssel als base64url (applicationServerKey der Oberfläche)."""
    punkt = (await vapid()).public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return base64.urlsafe_b64encode(punkt).rstrip(b"=").decode()


def thema(tag: str) -> str:
    """Topic-Kopf (höchstens 32 Zeichen base64url): eine noch nicht zugestellte Meldung gleichen Themas ersetzt
    der Push-Dienst, etwa eine ältere Regenstufe."""
    return base64.urlsafe_b64encode(hashlib.sha256(tag.encode()).digest()).rstrip(b"=").decode()[:32]


async def sende(endpunkt: str, p256dh: str, auth: str, nutzlast: dict, ttl: int, dringend: bool) -> Versand:
    """Eine Mitteilung senden. "weg": das Abo gibt es nicht mehr (404/410), es wird gelöscht."""
    try:
        await webpush_async(
            subscription_info={"endpoint": endpunkt, "keys": {"p256dh": p256dh, "auth": auth}},
            data=json.dumps(nutzlast, ensure_ascii=False),
            vapid_private_key=await vapid(),
            vapid_claims={"sub": settings.push_kontakt},
            ttl=ttl,
            timeout=20,
            headers={"Urgency": "high" if dringend else "normal", "Topic": thema(str(nutzlast.get("tag", "")))},
        )
        return "ok"
    except WebPushException as fehler:
        if fehler.status_code in (404, 410):
            return "weg"
        log.warning("Push an %s gescheitert: %s", endpunkt[:60], fehler.message)
        return "fehler"
    except Exception as fehler:  # Netz, Zeitüberschreitung: beim nächsten Takt wieder
        log.warning("Push an %s gescheitert: %s", endpunkt[:60], fehler)
        return "fehler"
