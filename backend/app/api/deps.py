from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.ai import AIEngine
from app.services.artifact import ArtifactEngine
from app.services.knowledge import KnowledgeEngine

def knowledge(session: AsyncSession = Depends(get_session)) -> KnowledgeEngine: return KnowledgeEngine(session)
def artifact(session: AsyncSession = Depends(get_session)) -> ArtifactEngine: return ArtifactEngine(session)
def ai() -> AIEngine: return AIEngine()
