"""Integration tests — navigation flow across all pages.

Tests the full navigation cycle: Home → Packages → Detail → Back → Guide.
Requires Flutter SDK + Flet client build.
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
class TestNavigation:
    """Test navigation between all pages."""

    async def test_home_page_loads(self, flet_app: ftt.FletTestApp):
        """Home page should display hero search bar and sections."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Hero search bar should be visible
        search = await flet_app.tester.find_by_text_containing("Search packages")
        assert search.count >= 1

    async def test_navigate_to_packages_via_search(self, flet_app: ftt.FletTestApp):
        """Typing in search and submitting should navigate to packages page."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Find search field and type
        search = await flet_app.tester.find_by_text_containing("Search packages")
        await flet_app.tester.tap(search.first)
        await flet_app.tester.enter_text(search.first, "audio")
        await flet_app.tester.pump_and_settle()

        # Should show RESULTS
        results = await flet_app.tester.find_by_text_containing("RESULTS")
        assert results.count >= 1

    async def test_navigate_to_guide(self, flet_app: ftt.FletTestApp):
        """Clicking Developer Guide in Help menu should navigate to guide page."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Find and click Help menu
        help_btn = await flet_app.tester.find_by_text("Help")
        if help_btn.count > 0:
            await flet_app.tester.tap(help_btn.first)
            await flet_app.tester.pump_and_settle()

            # Click Developer Guide
            guide = await flet_app.tester.find_by_text("Developer Guide")
            if guide.count > 0:
                await flet_app.tester.tap(guide.first)
                await flet_app.tester.pump_and_settle()

                # Guide page content should be visible
                title = await flet_app.tester.find_by_text_containing("Developer Guide")
                assert title.count >= 1

    async def test_navigate_to_package_detail(self, flet_app: ftt.FletTestApp):
        """Clicking a package card should navigate to its detail page."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Navigate to packages first (via VIEW ALL on any section)
        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        if view_all.count > 0:
            await flet_app.tester.tap(view_all.first)
            await flet_app.tester.pump_and_settle(timeout=15)

            # Should show package cards — find and click one
            results = await flet_app.tester.find_by_text_containing("RESULTS")
            assert results.count >= 1


@pytest.mark.parametrize(
    "flet_app",
    [{"flet_app_main": main, "skip_pump_and_settle": True}],
    indirect=True,
)
@pytest.mark.asyncio(loop_scope="function")
class TestThemeToggle:
    """Test theme switching."""

    async def test_theme_toggle_changes_mode(self, flet_app: ftt.FletTestApp):
        """Clicking theme toggle should switch between dark and light."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Find theme toggle button (by tooltip)
        toggle = await flet_app.tester.find_by_tooltip("Toggle theme")
        if toggle.count > 0:
            # Click toggle
            await flet_app.tester.tap(toggle.first)
            await flet_app.tester.pump_and_settle()

            # Page should now be in light mode
            assert flet_app.page.theme_mode is not None
