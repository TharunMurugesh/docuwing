from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.events import event_bus
router = APIRouter(prefix="/api/projects", tags=["events"])
@router.get("/{project_id}/events")
async def events(project_id: str): return StreamingResponse(event_bus.subscribe(project_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
