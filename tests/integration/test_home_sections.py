"""Integration tests — home page sections.

Tests that all home sections load correctly with real data from the index.
"""

import flet.testing as ftt
import pytest

from main import main


@pytest.mark.parametrize(
    "flet_app",
    [{"flet_app_main": main, "skip_pump_and_settle": True}],
    indirect=True,
)
@pytest.mark.asyncio(loop_scope="function")
class TestHomeSections:
    """Test home page sections load with real data."""

    async def test_official_section_visible(self, flet_app: ftt.FletTestApp):
        """Official Flet Extensions section should display."""
        await flet_app.tester.pump_and_settle(timeout=30)

        title = await flet_app.tester.find_by_text_containing("Official Flet Extensions")
        assert title.count >= 1

    async def test_trending_section_visible(self, flet_app: ftt.FletTestApp):
        """Trending packages section should display."""
        await flet_app.tester.pump_and_settle(timeout=30)

        title = await flet_app.tester.find_by_text_containing("Trending")
        assert title.count >= 1

    async def test_services_section_visible(self, flet_app: ftt.FletTestApp):
        """Services section should display."""
        await flet_app.tester.pump_and_settle(timeout=30)

        title = await flet_app.tester.find_by_text_containing("Services")
        assert title.count >= 1

    async def test_ui_controls_section_visible(self, flet_app: ftt.FletTestApp):
        """UI Controls section should display."""
        await flet_app.tester.pump_and_settle(timeout=30)

        title = await flet_app.tester.find_by_text_containing("UI Controls")
        assert title.count >= 1

    async def test_view_all_buttons_exist(self, flet_app: ftt.FletTestApp):
        """Each section should have a VIEW ALL button."""
        await flet_app.tester.pump_and_settle(timeout=30)

        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        # At least 4 sections should have VIEW ALL
        assert view_all.count >= 4

    async def test_package_cards_have_names(self, flet_app: ftt.FletTestApp):
        """Package cards should display package names."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Official packages like flet-audio should appear
        flet_pkg = await flet_app.tester.find_by_text_containing("flet-")
        assert flet_pkg.count >= 1

    async def test_footer_visible(self, flet_app: ftt.FletTestApp):
        """Footer should be visible at the bottom."""
        await flet_app.tester.pump_and_settle(timeout=60)

        # Footer has icon buttons for Discord, GitHub, etc.
        discord = await flet_app.tester.find_by_tooltip("Discord")
        assert discord.count >= 1
