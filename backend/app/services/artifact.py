from pathlib import Path
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models import ArtifactVersion, Result


class ArtifactEngine:
    def __init__(self, session: AsyncSession): self.session = session; self.settings = get_settings()
    async def create_markdown(self, project_id: str, title: str, content: str) -> Result:
        result = Result(project_id=project_id, kind="report", title=title); self.session.add(result); await self.session.flush()
        version_number = (await self.session.scalar(select(func.max(ArtifactVersion.version_number)).where(ArtifactVersion.result_id == result.id)) or 0) + 1
        directory = self.settings.storage_root / "projects" / project_id / "artifacts" / result.id / f"v{version_number}"; directory.mkdir(parents=True, exist_ok=True)
        path = directory / "report.md"; path.write_text(content, encoding="utf-8")
        version = ArtifactVersion(result_id=result.id, version_number=version_number, storage_path=str(path), format="markdown"); self.session.add(version); await self.session.flush(); result.latest_version_id = version.id; await self.session.commit()
        return result
