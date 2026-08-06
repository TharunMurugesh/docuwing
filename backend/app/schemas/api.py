from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ApiModel): name: str = Field(min_length=1, max_length=200)
class ProjectOut(ApiModel): id: str; name: str; created_at: datetime
class DocumentOut(ApiModel): id: str; project_id: str; filename: str; mime_type: str; status: str; page_count: int | None; created_at: datetime
class ChatRequest(ApiModel): text: str = Field(min_length=1, max_length=50000); session_id: str | None = None
class MessageOut(ApiModel): id: str; role: str; content: str; citations: list = []; created_at: datetime
class ResultOut(ApiModel): id: str; project_id: str; kind: str; title: str; latest_version_id: str | None; created_at: datetime
class VersionOut(ApiModel): id: str; result_id: str; version_number: int; storage_path: str; format: str; created_at: datetime
class JobOut(ApiModel): id: str; project_id: str; job_type: str; status: str; progress: float; error: str | None
