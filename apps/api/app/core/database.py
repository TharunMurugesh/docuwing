"""Database session management for the App layer."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import DatabaseSettings


def create_engine(settings: DatabaseSettings | None = None):
    """Create the async SQLAlchemy engine."""
    if settings is None:
        settings = DatabaseSettings()

    return create_async_engine(
        settings.url,
        pool_size=settings.pool_size,
        max_overflow=settings.pool_overflow,
        echo=settings.echo,
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the engine."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Default engine and session factory (initialized at import time for convenience)
_engine = create_engine()
_session_factory = create_session_factory(_engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency-injectable async session generator."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
