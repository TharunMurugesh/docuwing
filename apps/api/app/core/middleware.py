"""Request middleware — correlation ID injection and request timing.

Every incoming request gets a unique request_id (or uses one from the
X-Request-ID header if provided). The ID is injected into structlog's
contextvars so all log entries within a request carry the same correlation ID.
"""

from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject a unique request_id into every request's logging context."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Use caller-provided request ID or generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind to structlog contextvars for the duration of this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception("unhandled_exception")
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Echo the request_id back in the response header
        response.headers["X-Request-ID"] = request_id

        return response
