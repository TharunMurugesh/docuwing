"""Feature flags — table + cached read API.

Simple boolean feature flags stored in the App schema's feature_flags table.
Read-through cache avoids per-request DB queries.
"""

from __future__ import annotations

import time
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Shared declarative base for App-schema models."""

    pass


class FeatureFlag(Base):
    """Feature flag model — App schema."""

    __tablename__ = "feature_flags"
    __table_args__ = {"schema": "app"}

    name: Mapped[str] = mapped_column(sa.String(255), primary_key=True)
    enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[Any] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )


class FeatureFlagService:
    """Cached feature flag read API.

    Caches flag values in memory with a configurable TTL to avoid
    per-request database queries while still allowing runtime changes.
    """

    def __init__(self, cache_ttl_seconds: int = 60) -> None:
        self._cache: dict[str, tuple[bool, float]] = {}
        self._cache_ttl = cache_ttl_seconds

    def _is_cached(self, name: str) -> bool:
        if name not in self._cache:
            return False
        _, cached_at = self._cache[name]
        return (time.time() - cached_at) < self._cache_ttl

    async def get_flag(self, name: str, session: Any, default: bool = False) -> bool:
        """Get a feature flag value, using cache when available.

        Args:
            name: Flag name.
            session: SQLAlchemy async session.
            default: Default value if flag doesn't exist.

        Returns:
            Whether the feature is enabled.
        """
        if self._is_cached(name):
            cached_value, _ = self._cache[name]
            return bool(cached_value)

        try:
            result = await session.execute(
                sa.select(FeatureFlag.enabled).where(FeatureFlag.name == name)
            )
            row = result.scalar_one_or_none()

            if row is None:
                logger.debug("feature_flag_not_found", flag=name, default=default)
                return default

            self._cache[name] = (row, time.time())
            return row
        except Exception:
            logger.warning("feature_flag_read_error", flag=name, default=default)
            return default

    def invalidate(self, name: str | None = None) -> None:
        """Invalidate cached flag(s).

        Args:
            name: Specific flag to invalidate, or None to clear all.
        """
        if name is None:
            self._cache.clear()
        else:
            self._cache.pop(name, None)


# Module-level singleton
feature_flags = FeatureFlagService()
