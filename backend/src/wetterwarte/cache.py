"""Schlanker Redis-Hot-Cache. Faellt bei Nichterreichbarkeit still auf None zurueck."""

import json

from redis import asyncio as aioredis

from .config import settings

_redis = aioredis.from_url(settings.redis_url, decode_responses=True)


async def hole(schluessel: str) -> dict | None:
    try:
        roh = await _redis.get(schluessel)
        return json.loads(roh) if roh else None
    except Exception:
        return None


async def setze(schluessel: str, wert: object, ttl: int) -> None:
    try:
        await _redis.set(schluessel, json.dumps(wert), ex=ttl)
    except Exception:
        pass
