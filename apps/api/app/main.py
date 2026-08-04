"""Docuwing API — FastAPI application entry point.

Phase 0 deliverable: health check only, structured logging, OTel scaffolding.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestIdMiddleware
from app.core.observability import setup_telemetry
from app.core.settings import AppSettings

settings = AppSettings()
obs_settings = settings.observability()

# Initialize logging and telemetry before app creation
setup_logging(log_level=obs_settings.log_level, log_format=obs_settings.log_format)
setup_telemetry(
    service_name=obs_settings.service_name,
    exporter_type=obs_settings.exporter,
    otlp_endpoint=obs_settings.otlp_endpoint,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown hooks."""
    logger.info(
        "app_starting",
        environment=settings.environment,
        debug=settings.debug,
    )
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title="Docuwing API",
    description="Transform unstructured documents into structured, actionable knowledge.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware (order matters — outermost first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, Any]:
    """Health check endpoint.

    Returns service status and version. Used by Docker health checks
    and load balancers.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "docuwing-api",
    }
