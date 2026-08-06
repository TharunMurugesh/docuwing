import time
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routers import chat, documents, events, jobs, projects, results
from app.core.config import get_settings
from app.core.errors import DocuwingError
from app.db.session import engine
from app.models import Base
from app.workers.runner import job_runner

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
    await job_runner.start(); yield; await job_runner.stop(); await engine.dispose()

app = FastAPI(title="Docuwing", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[get_settings().cors_origin], allow_methods=["*"], allow_headers=["*"])
@app.middleware("http")
async def request_metadata(request: Request, call_next):
    started = time.perf_counter(); response = await call_next(request); response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", str(uuid4())); response.headers["X-Response-Time-Ms"] = str(round((time.perf_counter()-started)*1000)); return response
@app.exception_handler(DocuwingError)
async def known_error(_: Request, error: DocuwingError): return JSONResponse(status_code=error.status_code, content={"error": {"code": error.code, "message": error.message}})
@app.get("/api/health", tags=["health"])
async def health(): return {"status": "ok"}
for router in (projects.router, documents.router, chat.router, results.router, jobs.router, events.router): app.include_router(router)
