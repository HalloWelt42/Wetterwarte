"""FastAPI-Anwendung der Wetterwarte."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import recorder
from .config import settings
from .db import dispose_engine, init_db
from .migrationen import migriere_tile_ids
from .routers import archiv, aufzeichnung, dienste, health, kachel, kompat, layouts, orte, radar, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await migriere_tile_ids()  # einmalig: kollidierende Kachel-IDs -> eindeutige UUIDs
    aufgabe = asyncio.create_task(recorder.schleife())
    yield
    aufgabe.cancel()
    await dispose_engine()


app = FastAPI(
    title="Wetterwarte",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(orte.router, prefix="/api/v1")
app.include_router(layouts.router, prefix="/api/v1")
app.include_router(archiv.router, prefix="/api/v1")
app.include_router(dienste.router, prefix="/api/v1")
app.include_router(aufzeichnung.router, prefix="/api/v1")
app.include_router(radar.router, prefix="/api/v1")
app.include_router(kachel.router, prefix="/api/v1")
# Kompatibilitaets-Schicht der alten weathercache-API (fuer bestehende Konsumenten).
app.include_router(kompat.router, prefix="/api/v1")
