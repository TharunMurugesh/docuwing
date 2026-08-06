from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import NotFoundError
from app.db.session import get_session
from app.models import ArtifactVersion, Result
from app.schemas.api import ResultOut, VersionOut

router = APIRouter(prefix="/api/results", tags=["results"])
@router.get("/{result_id}", response_model=ResultOut)
async def get_result(result_id: str, session: AsyncSession = Depends(get_session)):
    item = await session.get(Result, result_id)
    if not item: raise NotFoundError("Result not found")
    return item
@router.get("/{result_id}/versions", response_model=list[VersionOut])
async def versions(result_id: str, session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(ArtifactVersion).where(ArtifactVersion.result_id == result_id).order_by(ArtifactVersion.version_number.desc()))).all()
@router.get("/{result_id}/versions/{number}/export")
async def export(result_id: str, number: int, session: AsyncSession = Depends(get_session)):
    version = await session.scalar(select(ArtifactVersion).where(ArtifactVersion.result_id == result_id, ArtifactVersion.version_number == number))
    if not version or not Path(version.storage_path).is_file(): raise NotFoundError("Artifact version not found")
    return FileResponse(version.storage_path, filename=Path(version.storage_path).name)
