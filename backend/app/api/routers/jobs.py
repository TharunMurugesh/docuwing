from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import NotFoundError
from app.db.session import get_session
from app.models import Job
from app.schemas.api import JobOut
router = APIRouter(prefix="/api/jobs", tags=["jobs"])
@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, session: AsyncSession = Depends(get_session)):
    job = await session.get(Job, job_id)
    if not job: raise NotFoundError("Job not found")
    return job
