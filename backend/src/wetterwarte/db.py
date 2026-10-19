"""Asynchrone Datenbank-Anbindung (SQLModel/SQLAlchemy + asyncpg)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-Dependency: liefert eine Session pro Anfrage."""
    async with SessionLocal() as session:
        yield session


async def dispose_engine() -> None:
    await engine.dispose()


async def init_db() -> None:
    """Schema per Migration auf den neuesten Stand bringen, bei leerer Datenbank Standard-Layouts
    und Beispiel-Orte anlegen."""
    from sqlmodel import select

    from . import schema
    from .models.layout import Layout
    from .models.ort import Ort
    from .orte import ORTE

    async with engine.begin() as conn:
        await conn.run_sync(schema.aktualisiere)

    async with SessionLocal() as session:
        # Erster Start = noch kein Profil. Nur dann Standard-Profile und ein paar generische
        # Beispiel-Orte anlegen; danach pflegt der Nutzer beides selbst (auch eine bewusst
        # geleerte Ortsliste bleibt leer).
        if (await session.execute(select(Layout))).scalars().first() is not None:
            return
        for name, standard in [("Zuhause", True), ("Garten", False), ("Reise", False), ("Unwetter", False)]:
            session.add(Layout(name=name, ist_standard=standard, daten=[]))
        if (await session.execute(select(Ort))).scalars().first() is None:
            for i, (slug, o) in enumerate(ORTE.items()):
                session.add(
                    Ort(
                        slug=slug,
                        name=o["name"],
                        region=o["region"],
                        land="Deutschland",
                        lat=o["lat"],
                        lon=o["lon"],
                        reihenfolge=i,
                        ist_start=(i == 0),
                    )
                )
        await session.commit()
