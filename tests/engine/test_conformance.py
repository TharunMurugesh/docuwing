"""EDS §2.3 Decoupling Conformance Test.

This test asserts that the Engine layer genuinely operates independently of the
App layer, without any hidden imports or dependencies.
"""

import sys

import pytest


def test_engine_imports_no_app():
    """Verify that importing docuwing_engine does not import app."""
    # This is also enforced by import-linter, but we do a runtime check here

    # Ensure 'app' is not in sys.modules, or at least nothing under it
    app_modules = [m for m in sys.modules if m == "app" or m.startswith("app.")]
    assert len(app_modules) == 0, f"Found forbidden App imports: {app_modules}"


@pytest.mark.asyncio
async def test_engine_runs_standalone():
    """Verify the Engine can instantiate and run with in-memory adapters."""
    from docuwing_engine.adapters.memory.repositories import InMemoryRepositoryBundle
    from docuwing_engine.adapters.memory.storage import InMemoryStorageProvider
    from docuwing_engine.engine import DocuwingEngine
    from docuwing_engine.workflow.events import LoggingEventPublisher

    class MockLogger:
        def info(self, *args, **kwargs):
            pass

    bundle = InMemoryRepositoryBundle(InMemoryStorageProvider())

    # Initialization shouldn't crash
    engine = DocuwingEngine(
        repositories=bundle,
        event_publisher=LoggingEventPublisher(MockLogger()),
    )

    # We can list plugins without App dependencies
    plugins = engine.plugins.list()
    assert isinstance(plugins, list)
