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
    """Tabellen anlegen und bei leerer Datenbank Standard-Layouts anlegen.

    Fuer den Anfang genuegt create_all; spaeter uebernehmen Alembic-Migrationen.
    """
    from sqlmodel import SQLModel, select

    from .models.aufzeichnung import AufzeichnungOrt  # noqa: F401 - Tabelle registrieren
    from .models.klima import KlimaNormale  # noqa: F401 - Tabelle registrieren
    from .models.layout import Layout
    from .models.messwert import Messwert  # noqa: F401 - Tabelle registrieren
    from .models.ort import Ort
    from .orte import ORTE

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with SessionLocal() as session:
        vorhanden = (await session.execute(select(Layout))).scalars().first()
        if vorhanden is None:
            for name, standard in [("Zuhause", True), ("Garten", False), ("Reise", False), ("Unwetter", False)]:
                session.add(Layout(name=name, ist_standard=standard, daten=[]))
            await session.commit()

        # Beim ersten Start ein paar generische Beispiel-Orte anlegen; danach
        # pflegt der Nutzer die Liste selbst per Suche (Quelle der Wahrheit: DB).
        ort_vorhanden = (await session.execute(select(Ort))).scalars().first()
        if ort_vorhanden is None:
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
