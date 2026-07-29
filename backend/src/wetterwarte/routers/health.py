"""Health-Endpunkt fuer Betrieb und Health-Probe."""

from fastapi import APIRouter

from ..config import settings
from ..schemas.envelope import wrap

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return wrap({"status": "ok", "version": settings.version})
