"""Shared fixtures for all tests.

Integration tests require Flutter SDK + Flet client build.
They are auto-skipped when the environment is not available.

Run unit tests only:
    uv run pytest tests/unit/ -v

Run integration tests (desktop Linux — default):
    uv run pytest tests/integration/ -v

Run integration tests (Android emulator/device):
    FLET_TEST_PLATFORM=android FLET_TEST_DEVICE=emulator-5554 \
        uv run pytest tests/integration/ -v

Run all:
    uv run pytest tests/ -v

Supported platforms: Linux desktop, macOS, Windows, Android (emulator/device), iOS.
Web (Chrome) is NOT supported by Flutter integration tests yet.
"""

import os
import shutil
from pathlib import Path

import pytest

FLUTTER_CLIENT_DIR = Path(
    os.getenv("FLET_CLIENT_DIR", "/data/projects/python/flet/client")
).resolve()
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

_flutter_available = shutil.which("flutter") is not None and FLUTTER_CLIENT_DIR.exists()


def pytest_collection_modifyitems(config, items):
    """Auto-skip integration tests when Flutter SDK is not available."""
    if _flutter_available:
        return
    skip_marker = pytest.mark.skip(reason="Flutter SDK or client not available")
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(skip_marker)


# --- Integration test fixture ---

try:
    import pytest_asyncio

    @pytest_asyncio.fixture(scope="function")
    async def flet_app(request):
        """Fixture that starts the Flet app for integration testing.

        Supports desktop (default) and Android via env vars:
            FLET_TEST_PLATFORM=android      → target Android
            FLET_TEST_DEVICE=emulator-5554  → Android emulator or device ID
        """
        import flet.testing as ftt
        from flet.controls.context import _context_page, context

        params = getattr(request, "param", {})

        app = ftt.FletTestApp(
            flutter_app_dir=FLUTTER_CLIENT_DIR,
            test_path=str(request.fspath),
            flet_app_main=params.get("flet_app_main"),
            skip_pump_and_settle=params.get("skip_pump_and_settle", False),
            assets_dir=str(ASSETS_DIR),
            disable_fvm=True,
        )
        await app.start()
        token = _context_page.set(app.page)
        context.reset_auto_update()
        try:
            yield app
        finally:
            _context_page.reset(token)
            await app.teardown()

except ImportError:
    pass
