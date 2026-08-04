"""MVP application API. Persistence is deliberately replaceable behind this service."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.settings import AuthSettings

router = APIRouter(prefix="/v1")
_users: dict[str, dict[str, Any]] = {"demo@docuwing.local": {"password": "demo", "role": "owner", "organization": "demo"}}
_projects: dict[str, dict[str, Any]] = {}
_documents: dict[str, dict[str, Any]] = {}
_schemas: dict[str, dict[str, Any]] = {}

class Login(BaseModel): email: str; password: str
class ProjectIn(BaseModel): name: str
class SchemaIn(BaseModel): project_id: str; name: str; fields: list[dict[str, Any]] = Field(default_factory=list)
class FieldPatch(BaseModel): value: Any | None = None; confirmed: bool = False; notes: str = ""
class ChatIn(BaseModel): question: str

def _token(email: str) -> str:
    expires = (datetime.now(UTC) + timedelta(minutes=AuthSettings().access_token_expire_minutes)).isoformat()
    body = f"{email}|{expires}"; sig = hmac.new(AuthSettings().secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}|{sig}"

def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401, "Authentication required")
    try:
        email, expires, sig = authorization[7:].rsplit("|", 2); body = f"{email}|{expires}"; expected = hmac.new(AuthSettings().secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or datetime.fromisoformat(expires) < datetime.now(UTC): raise ValueError
        return {"email": email, **_users[email]}
    except (KeyError, ValueError): raise HTTPException(401, "Invalid or expired token")

@router.post("/auth/login")
async def login(payload: Login) -> dict[str, str]:
    user = _users.get(payload.email)
    if not user or not secrets.compare_digest(user["password"], payload.password): raise HTTPException(401, "Invalid credentials")
    return {"access_token": _token(payload.email), "refresh_token": _token(payload.email), "token_type": "bearer"}

@router.post("/auth/refresh")
async def refresh(user: dict[str, Any] = Depends(current_user)) -> dict[str, str]: return {"access_token": _token(user["email"]), "token_type": "bearer"}

@router.get("/projects")
async def list_projects(user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]: return [p for p in _projects.values() if p["organization"] == user["organization"]]

@router.post("/projects", status_code=201)
async def create_project(payload: ProjectIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    project = {"id": str(uuid.uuid4()), "name": payload.name, "organization": user["organization"], "collections": []}; _projects[project["id"]] = project; return project

def _project(project_id: str, user: dict[str, Any]) -> dict[str, Any]:
    project = _projects.get(project_id)
    if not project or project["organization"] != user["organization"]: raise HTTPException(404, "Project not found")
    return project

@router.get("/projects/{project_id}/collections")
async def list_collections(project_id: str, user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]: return _project(project_id, user)["collections"]

@router.post("/projects/{project_id}/collections", status_code=201)
async def create_collection(project_id: str, payload: ProjectIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    collection = {"id": str(uuid.uuid4()), "name": payload.name}; _project(project_id, user)["collections"].append(collection); return collection

@router.post("/projects/{project_id}/documents", status_code=202)
async def upload(project_id: str, file: UploadFile = File(...), user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    _project(project_id, user); document_id = str(uuid.uuid4()); raw = await file.read()
    _documents[document_id] = {"id": document_id, "project_id": project_id, "filename": file.filename, "status": "ready", "content": raw.decode(errors="replace"), "fields": []}
    return {"document_id": document_id, "status_url": f"/v1/documents/{document_id}/status"}

def _document(document_id: str, user: dict[str, Any]) -> dict[str, Any]:
    document = _documents.get(document_id)
    if not document: raise HTTPException(404, "Document not found")
    _project(document["project_id"], user); return document

@router.get("/documents/{document_id}")
async def get_document(document_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]: return _document(document_id, user)
@router.get("/documents/{document_id}/status")
async def status(document_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]: return {"status": _document(document_id, user)["status"]}
@router.get("/documents/{document_id}/content")
async def content(document_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]: return {"content": _document(document_id, user)["content"]}

@router.post("/schemas", status_code=201)
async def create_schema(payload: SchemaIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    _project(payload.project_id, user); schema = {"id": str(uuid.uuid4()), **payload.model_dump(), "version": 1}; _schemas[schema["id"]] = schema; return schema
@router.get("/schemas/{schema_id}")
async def get_schema(schema_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    schema = _schemas.get(schema_id)
    if not schema: raise HTTPException(404, "Schema not found")
    _project(schema["project_id"], user); return schema

@router.post("/documents/{document_id}/extract", status_code=202)
async def extract(document_id: str, schema_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    doc = _document(document_id, user); schema = await get_schema(schema_id, user); doc["fields"] = [{"id": str(uuid.uuid4()), "field_name": field["name"], "value": None, "validation_state": "needs_review", "confidence": 0.0, "human_confirmed": False} for field in schema["fields"]]; return {"status": "queued", "document_id": document_id}

@router.get("/documents/{document_id}/extraction/{schema_id}")
async def extraction(document_id: str, schema_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]: return {"fields": _document(document_id, user)["fields"]}
@router.patch("/documents/{document_id}/extraction/{schema_id}/fields/{field_id}")
async def patch_field(document_id: str, schema_id: str, field_id: str, payload: FieldPatch, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    field = next((f for f in _document(document_id, user)["fields"] if f["id"] == field_id), None)
    if field is None: raise HTTPException(404, "Field not found")
    if payload.value is not None: field["value"] = payload.value
    field.update({"human_confirmed": payload.confirmed, "validation_state": "human_confirmed" if payload.confirmed else field["validation_state"], "review_notes": payload.notes}); return field

@router.post("/documents/{document_id}/chat")
async def chat(document_id: str, payload: ChatIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    doc = _document(document_id, user); return {"answer": "No grounded field matched your question." if not doc["fields"] else f"Reviewed fields: {', '.join(f['field_name'] for f in doc['fields'])}", "citations": []}
@router.post("/documents/{document_id}/{output_format}")
async def generate_output(document_id: str, output_format: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    doc = _document(document_id, user)
    allowed = {"summary", "timeline", "graph", "diagram", "chart"}
    if output_format not in allowed: raise HTTPException(404, "Unknown output format")
    return {"format": output_format, "content": f"{output_format.title()} for {doc['filename']}\n\n" + "\n".join(f"{field['field_name']}: {field['value']}" for field in doc["fields"])}
@router.get("/documents/{document_id}/export")
async def export(document_id: str, format: str = "json", user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    doc = _document(document_id, user)
    return {"format": format, "document": doc}
@router.get("/search")
async def search(q: str, project_id: str, user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    _project(project_id, user); return [{"id": d["id"], "filename": d["filename"]} for d in _documents.values() if d["project_id"] == project_id and q.lower() in d["content"].lower()]
