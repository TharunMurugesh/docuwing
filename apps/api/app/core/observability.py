"""OpenTelemetry SDK initialization.

Phase 0 uses a console exporter (no-op in terms of external dependencies).
Swap to OTLP exporter via config when a collector is available.
"""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_telemetry(
    service_name: str = "docuwing-api",
    exporter_type: str = "console",
    otlp_endpoint: str = "http://localhost:4317",
) -> None:
    """Initialize OpenTelemetry tracing.

    Args:
        service_name: The service name for trace identification.
        exporter_type: 'console' for dev, 'otlp' for production.
        otlp_endpoint: OTLP collector endpoint (used only when exporter_type='otlp').
    """
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "0.1.0",
        }
    )

    provider = TracerProvider(resource=resource)

    if exporter_type == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))
            logger.info("otel_initialized", exporter="otlp", endpoint=otlp_endpoint)
        except ImportError:
            logger.warning("otlp_exporter_unavailable", fallback="console")
            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        # Console exporter for development — prints spans to stdout
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        logger.info("otel_initialized", exporter="console")

    trace.set_tracer_provider(provider)


def get_tracer(name: str = "docuwing") -> trace.Tracer:
    """Get an OpenTelemetry tracer instance."""
    return trace.get_tracer(name)
