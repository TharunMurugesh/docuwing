from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import NotFoundError
from app.db.session import get_session
from app.models import Document, Project, Result
from app.schemas.api import DocumentOut, ProjectCreate, ProjectOut, ResultOut

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("", response_model=ProjectOut, status_code=201)
async def create(body: ProjectCreate, session: AsyncSession = Depends(get_session)):
    project = Project(name=body.name); session.add(project); await session.commit(); await session.refresh(project); return project

@router.get("", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Project).order_by(Project.updated_at.desc()))).all()

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, session: AsyncSession = Depends(get_session)):
    project = await session.get(Project, project_id)
    if not project: raise NotFoundError("Project not found")
    return project

@router.delete("/{project_id}", status_code=204)
async def remove(project_id: str, session: AsyncSession = Depends(get_session)):
    project = await session.get(Project, project_id)
    if not project: raise NotFoundError("Project not found")
    await session.delete(project); await session.commit()

@router.get("/{project_id}/documents", response_model=list[DocumentOut])
async def documents(project_id: str, session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc()))).all()

@router.get("/{project_id}/results", response_model=list[ResultOut])
async def results(project_id: str, session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Result).where(Result.project_id == project_id).order_by(Result.created_at.desc()))).all()
