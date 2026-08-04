"""Shared OpenTelemetry configuration utilities.

Used by both the API app and engine for consistent trace/metric configuration.
"""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def create_tracer_provider(
    service_name: str,
    service_version: str = "0.1.0",
    exporter_type: str = "console",
) -> TracerProvider:
    """Create and return a configured TracerProvider.

    Args:
        service_name: Name of the service for trace identification.
        service_version: Version of the service.
        exporter_type: 'console' for dev, 'otlp' for production.

    Returns:
        Configured TracerProvider.
    """
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        }
    )

    provider = TracerProvider(resource=resource)

    if exporter_type == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return provider
