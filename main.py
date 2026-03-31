"""Application entry point — Composition Root.

Uses page.render_views() with ft.create_context() for proper declarative navigation.
URL routing: /, /guide, /packages, /packages?q=query, /packages/package-name

Navigation flow (unidirectional):
  navigate(target) → NavigationService.push(url) → on_route_change → _handle_route → load data
"""

import logging

import flet as ft

from src.presentation.app import App
from src.presentation.hooks.use_packages import (
    load_home_data,
    load_package_detail_by_name,
    search_packages,
)
from src.presentation.hooks.use_theme import toggle_theme_mode
from src.presentation.navigation.app_router import parse_route
from src.presentation.navigation.navigation_service import NavigationService
from src.presentation.state_management.app_context import AppContextValue
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.app_theme import get_dark_theme, get_light_theme
from src.presentation.themes.colors import DARK_BG
from src.services.api_service import ApiService


def _patch_session_dispatch(session) -> None:
    """Gracefully handle events on controls that were replaced during re-render."""
    original_dispatch = session.dispatch_event

    async def safe_dispatch(control_id, event_name, event_data):
        control = session._Session__index.get(control_id)
        if control is None:
            return
        try:
            await original_dispatch(control_id, event_name, event_data)
        except Exception:
            logging.debug("Ignored event on detached %s(%s)", type(control).__name__, control_id)

    session.dispatch_event = safe_dispatch


def main(page: ft.Page) -> None:
    page.title = "Flet PKG - Package Discovery"
    page.theme = get_light_theme()
    page.dark_theme = get_dark_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.spacing = 0

    _patch_session_dispatch(page.session)

    # --- Dependency wiring ---
    app_state = AppState()
    api = ApiService()
    pkg_state = app_state.packages
    nav = NavigationService(page)
    prefs = ft.SharedPreferences()

    # --- Load saved preferences ---
    async def _load_preferences() -> None:
        is_dark = await prefs.get("is_dark")
        if is_dark is not None:
            app_state.is_dark = bool(is_dark)
            page.theme_mode = ft.ThemeMode.DARK if app_state.is_dark else ft.ThemeMode.LIGHT
            page.update()

        show_pypi_only = await prefs.get("show_pypi_only")
        if show_pypi_only is not None:
            app_state.show_pypi_only = bool(show_pypi_only)

        per_page = await prefs.get("per_page")
        if per_page is not None:
            pkg_state.per_page = int(per_page)

    page.run_task(_load_preferences)
    page.run_task(api.start_background_tasks)

    # --- Data loaders ---
    async def _load_home() -> None:
        app_state.current_page = "home"
        if pkg_state.home_data is None:
            await load_home_data(pkg_state, api, pypi_only=app_state.show_pypi_only)

    async def _load_detail(name: str) -> None:
        app_state.detail_package_name = name
        pkg_state.detail_package = None
        pkg_state.error = ""
        app_state.current_page = "detail"
        await load_package_detail_by_name(pkg_state, api, name)

    async def _load_search(
        query: str = "",
        sort: str = "default ranking",
        filter_type: str | None = None,
        official: bool = False,
        categories: list[str] | None = None,
        page_num: int = 1,
    ) -> None:
        pkg_state.search_query = query
        pkg_state.sort_by = sort
        pkg_state.filter_type = filter_type
        pkg_state.filter_official = official
        pkg_state.filter_categories = categories or []
        pkg_state.page_number = page_num
        app_state.current_page = "packages"
        await search_packages(pkg_state, api, query, page_num, pypi_only=app_state.show_pypi_only)

    # --- Route handling ---
    def _handle_route(route: str) -> None:
        if not nav.should_handle(route):
            return

        r = parse_route(route)

        if r.page == "home":
            page.run_task(_load_home)
        elif r.page == "guide":
            app_state.current_page = "guide"
        elif r.page == "packages":
            page.run_task(
                _load_search, r.query, r.sort, r.filter_type, r.official, r.categories, r.page_num
            )
        elif r.page == "detail":
            page.run_task(_load_detail, r.package_name)
        else:
            page.run_task(_load_home)

    # --- Action handlers ---
    def handle_navigate(target: str) -> None:
        nav.navigate(target)

    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state)
        page.run_task(prefs.set, "is_dark", app_state.is_dark)

    def handle_pypi_filter_toggle() -> None:
        app_state.show_pypi_only = not app_state.show_pypi_only
        page.run_task(prefs.set, "show_pypi_only", app_state.show_pypi_only)
        if app_state.current_page == "packages":
            page.run_task(
                _load_search,
                pkg_state.search_query,
                pkg_state.sort_by,
                pkg_state.filter_type,
                pkg_state.filter_official,
                pkg_state.filter_categories or None,
                pkg_state.page_number,
            )
        else:
            pkg_state.home_data = None
            page.run_task(_load_home)

    def handle_search(query: str = "") -> None:
        nav.navigate(f"packages:{query}")

    def handle_reload_packages() -> None:
        nav.push_packages_url(
            query=pkg_state.search_query,
            sort=pkg_state.sort_by,
            filter_type=pkg_state.filter_type,
            official=pkg_state.filter_official,
            categories=pkg_state.filter_categories or None,
            page_num=pkg_state.page_number,
        )
        page.run_task(
            _load_search,
            pkg_state.search_query,
            pkg_state.sort_by,
            pkg_state.filter_type,
            pkg_state.filter_official,
            pkg_state.filter_categories or None,
            pkg_state.page_number,
        )

    def handle_copy(text: str) -> None:
        page.run_task(ft.Clipboard().set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    # --- URL event handlers ---
    page.on_route_change = lambda e: _handle_route(e.route)
    page.on_view_pop = lambda _: _handle_route(page.route)

    # --- Context ---
    ctx_value = AppContextValue(
        state=app_state,
        api=api,
        navigate=handle_navigate,
        toggle_theme=handle_theme_toggle,
        toggle_pypi_filter=handle_pypi_filter_toggle,
        search=handle_search,
        reload_packages=handle_reload_packages,
        copy_to_clipboard=handle_copy,
    )

    # --- Initial load + render ---
    page.render_views(App, ctx_value, app_state)
    _handle_route(page.route)


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
    )
