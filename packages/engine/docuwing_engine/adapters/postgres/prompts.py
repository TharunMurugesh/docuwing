"""Postgres-backed prompt pointer repository."""

from __future__ import annotations

from typing import Any

from docuwing_engine.interfaces.repositories import PromptRepository


class PostgresPromptRepository(PromptRepository):
    """Postgres implementation for prompt pointers."""

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def get_active_pointer(self, task_type: str, model_id: str) -> str | None:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                SELECT version FROM engine.prompt_active_pointer
                WHERE task_type = :task_type AND model_id = :model_id
                """
            )
            result = await session.execute(stmt, {"task_type": task_type, "model_id": model_id})
            return str(result.scalar_one_or_none()) if result.scalar_one_or_none() is not None else None

    async def set_active_pointer(self, task_type: str, model_id: str, version: str) -> None:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                INSERT INTO engine.prompt_active_pointer (task_type, model_id, version)
                VALUES (:task_type, :model_id, :version)
                ON CONFLICT (task_type, model_id) DO UPDATE SET version = EXCLUDED.version
                """
            )
            await session.execute(
                stmt, {"task_type": task_type, "model_id": model_id, "version": version}
            )
            await session.commit()
