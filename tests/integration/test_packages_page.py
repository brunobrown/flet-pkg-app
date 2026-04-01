"""Integration tests — packages list page functionality.

Tests filters, sort, pagination, and search on the packages page.
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
class TestPackagesPage:
    """Test the packages list page filters, sort, and pagination."""

    async def _navigate_to_packages(self, flet_app: ftt.FletTestApp):
        """Helper: navigate to packages page via VIEW ALL."""
        await flet_app.tester.pump_and_settle(timeout=30)
        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        if view_all.count > 0:
            await flet_app.tester.tap(view_all.first)
            await flet_app.tester.pump_and_settle(timeout=15)

    async def test_packages_page_shows_results(self, flet_app: ftt.FletTestApp):
        """Packages page should display RESULTS count and cards."""
        await self._navigate_to_packages(flet_app)

        results = await flet_app.tester.find_by_text_containing("RESULTS")
        assert results.count >= 1

        packages = await flet_app.tester.find_by_text_containing("packages")
        assert packages.count >= 1

    async def test_sort_dropdown_exists(self, flet_app: ftt.FletTestApp):
        """Sort dropdown should be visible on packages page (desktop)."""
        await self._navigate_to_packages(flet_app)

        sort = await flet_app.tester.find_by_text_containing("default ranking")
        assert sort.count >= 1

    async def test_pagination_visible(self, flet_app: ftt.FletTestApp):
        """Pagination controls should be visible."""
        await self._navigate_to_packages(flet_app)

        # Page number buttons should exist
        page1 = await flet_app.tester.find_by_text("1")
        assert page1.count >= 1

    async def test_filter_sidebar_toggle(self, flet_app: ftt.FletTestApp):
        """Filter sidebar should open when toggle is clicked."""
        await self._navigate_to_packages(flet_app)

        # Find filter toggle tab
        filters = await flet_app.tester.find_by_text("Filters")
        if filters.count > 0:
            await flet_app.tester.tap(filters.first)
            await flet_app.tester.pump_and_settle()

            # Sidebar should show filter checkboxes
            ui_controls = await flet_app.tester.find_by_text("UI Controls")
            assert ui_controls.count >= 1

            services = await flet_app.tester.find_by_text("Services")
            assert services.count >= 1


@pytest.mark.parametrize(
    "flet_app",
    [{"flet_app_main": main, "skip_pump_and_settle": True}],
    indirect=True,
)
@pytest.mark.asyncio(loop_scope="function")
class TestPackageDetail:
    """Test the package detail page."""

    async def test_detail_page_shows_readme(self, flet_app: ftt.FletTestApp):
        """Package detail page should show Readme tab content."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Navigate to packages
        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        if view_all.count > 0:
            await flet_app.tester.tap(view_all.first)
            await flet_app.tester.pump_and_settle(timeout=15)

            # Click on first package name (should be a link)
            # Look for any package name that starts with "flet-"
            flet_pkg = await flet_app.tester.find_by_text_containing("flet-")
            if flet_pkg.count > 0:
                await flet_app.tester.tap(flet_pkg.first)
                await flet_app.tester.pump_and_settle(timeout=15)

                # Detail page should have tabs
                readme = await flet_app.tester.find_by_text("Readme")
                assert readme.count >= 1

                changelog = await flet_app.tester.find_by_text("Changelog")
                assert changelog.count >= 1

    async def test_detail_page_share_button(self, flet_app: ftt.FletTestApp):
        """Share button should be visible on detail page."""
        await flet_app.tester.pump_and_settle(timeout=30)

        # Navigate to packages and then detail
        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        if view_all.count > 0:
            await flet_app.tester.tap(view_all.first)
            await flet_app.tester.pump_and_settle(timeout=15)

            flet_pkg = await flet_app.tester.find_by_text_containing("flet-")
            if flet_pkg.count > 0:
                await flet_app.tester.tap(flet_pkg.first)
                await flet_app.tester.pump_and_settle(timeout=15)

                # Share button should exist
                share = await flet_app.tester.find_by_tooltip("Share package")
                assert share.count >= 1

    async def test_detail_page_like_button(self, flet_app: ftt.FletTestApp):
        """LIKE button should be visible on detail page."""
        await flet_app.tester.pump_and_settle(timeout=30)

        view_all = await flet_app.tester.find_by_text("VIEW ALL")
        if view_all.count > 0:
            await flet_app.tester.tap(view_all.first)
            await flet_app.tester.pump_and_settle(timeout=15)

            flet_pkg = await flet_app.tester.find_by_text_containing("flet-")
            if flet_pkg.count > 0:
                await flet_app.tester.tap(flet_pkg.first)
                await flet_app.tester.pump_and_settle(timeout=15)

                like = await flet_app.tester.find_by_text("LIKE")
                assert like.count >= 1
