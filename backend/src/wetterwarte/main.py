"""FastAPI-Anwendung der Wetterwarte."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import recorder
from .config import settings
from .db import dispose_engine, init_db
from .routers import archiv, health, layouts, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
app.include_router(layouts.router, prefix="/api/v1")
app.include_router(archiv.router, prefix="/api/v1")
