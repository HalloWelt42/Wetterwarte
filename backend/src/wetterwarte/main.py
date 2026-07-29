"""FastAPI-Anwendung der Wetterwarte."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .db import dispose_engine, init_db
from .routers import health, layouts, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
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
