import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ai, artifact, knowledge
from app.core.errors import NotFoundError
from app.db.session import get_session
from app.models import ChatSession, Message, Project
from app.schemas.api import ChatRequest, MessageOut
from app.services.ai import AIEngine
from app.services.artifact import ArtifactEngine
from app.services.knowledge import KnowledgeEngine

router = APIRouter(prefix="/api/projects/{project_id}", tags=["chat"])

def sse(event: str, data: dict) -> str: return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"

@router.post("/chat")
async def chat(project_id: str, body: ChatRequest, session: AsyncSession = Depends(get_session), engine: KnowledgeEngine = Depends(knowledge), inference: AIEngine = Depends(ai), artifacts: ArtifactEngine = Depends(artifact)):
    if not await session.get(Project, project_id): raise NotFoundError("Project not found")
    session_id = body.session_id
    if session_id:
        chat_session = await session.get(ChatSession, session_id)
        if not chat_session or chat_session.project_id != project_id: raise NotFoundError("Chat session not found")
    else:
        chat_session = ChatSession(project_id=project_id); session.add(chat_session); await session.flush(); session_id = chat_session.id
    session.add(Message(session_id=session_id, role="user", content=body.text)); await session.commit()
    async def stream():
        yield sse("status", {"stage": "retrieving", "session_id": session_id})
        context = await engine.retrieve(project_id, body.text)
        yield sse("sources", {"sources": [{k: source[k] for k in ("chunk_id", "document_id", "document", "sequence", "metadata")} for source in context]})
        answer = ""
        try:
            async for token in inference.stream_answer(body.text, context):
                answer += token; yield sse("token", {"text": token})
        except Exception as exc:
            yield sse("error", {"message": str(exc)}); return
        citations = [{"document_id": item["document_id"], "chunk_id": item["chunk_id"], "label": f"{item['document']} / {item['sequence']}"} for item in context]
        session.add(Message(session_id=session_id, role="assistant", content=answer, citations=citations)); await session.commit()
        artifact_ref = None
        if any(term in body.text.lower() for term in ("report", "export", "artifact")):
            result = await artifacts.create_markdown(project_id, "Generated report", answer); artifact_ref = {"id": result.id, "title": result.title, "kind": result.kind}
        yield sse("done", {"session_id": session_id, "citations": citations, "artifact": artifact_ref})
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.get("/chat/history", response_model=list[MessageOut])
async def history(project_id: str, session: AsyncSession = Depends(get_session)):
    sessions = (await session.scalars(select(ChatSession.id).where(ChatSession.project_id == project_id))).all()
    if not sessions: return []
    return (await session.scalars(select(Message).where(Message.session_id.in_(sessions)).order_by(Message.created_at))).all()
