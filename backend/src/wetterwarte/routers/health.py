"""Health-Endpunkt fuer Betrieb und Health-Probe."""

from fastapi import APIRouter

from ..config import aktuelle_version
from ..schemas.envelope import wrap

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    # Fassung frisch aus version.json, damit offene Oberflächen eine neue Fassung bemerken und neu laden.
    return wrap({"status": "ok", "version": aktuelle_version()})
