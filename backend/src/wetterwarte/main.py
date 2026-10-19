"""FastAPI-Anwendung der Wetterwarte."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from . import recorder
from .config import settings
from .db import dispose_engine, init_db
from .migrationen import aggregate_in_ortszeit, migriere_tile_ids, telefon_vorlagen
from .routers import archiv, aufzeichnung, dienste, health, kachel, kompat, layouts, orte, radar, weather


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # Schema per Migration aktuell, beim ersten Start Profile und Beispiel-Orte
    await migriere_tile_ids()  # einmalig: kollidierende Kachel-IDs -> eindeutige UUIDs
    await aggregate_in_ortszeit()  # einmalig nach der Umstellung auf Zeitzonen
    await telefon_vorlagen()  # Profile ohne Telefon-Layout bekommen die Vorlage
    aufgabe = asyncio.create_task(recorder.schleife())
    yield
    aufgabe.cancel()
    try:
        await aufgabe
    except asyncio.CancelledError:
        pass
    await dispose_engine()


app = FastAPI(
    title="Wetterwarte",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

# Antworten ab 1 KB komprimiert (Wetterdaten schrumpfen auf rund ein Viertel).
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
