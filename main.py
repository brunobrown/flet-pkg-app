"""Application entry point — Composition Root.

Uses page.render_views() with ft.create_context() for proper declarative navigation.
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
from src.presentation.state_management.app_context import AppContextValue
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.app_theme import get_dark_theme, get_light_theme
from src.presentation.themes.colors import DARK_BG
from src.services.api_service import ApiService


def _patch_session_dispatch(session) -> None:
    """Skip events on orphaned controls (parent chain doesn't reach Page)."""
    from flet.controls.page import Page

    original_dispatch = session.dispatch_event

    def _is_attached(control) -> bool:
        current = control
        while current is not None:
            if isinstance(current, Page):
                return True
            current = current.parent
        return False

    async def safe_dispatch(control_id, event_name, event_data):
        control = session._Session__index.get(control_id)
        if control and not _is_attached(control):
            logging.debug("Skipping event on orphaned %s(%s)", type(control).__name__, control_id)
            return
        await original_dispatch(control_id, event_name, event_data)

    session.dispatch_event = safe_dispatch


def main(page: ft.Page) -> None:
    page.title = "Flet PKG - Package Discovery"
    page.theme = get_light_theme()
    page.dark_theme = get_dark_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.spacing = 0

    # Guard orphaned control events
    _patch_session_dispatch(page.session)

    # --- Dependency wiring ---
    app_state = AppState()
    api = ApiService()
    pkg_state = app_state.packages

    # --- Data loaders ---
    async def _load_home() -> None:
        if pkg_state.home_data is None:
            await load_home_data(pkg_state, api, pypi_only=app_state.show_pypi_only)
        app_state.current_page = "home"

    async def _load_detail(name: str) -> None:
        app_state.detail_package_name = name
        pkg_state.detail_package = None
        pkg_state.error = ""
        await load_package_detail_by_name(pkg_state, api, name)
        # Navigate to detail even on error (page shows error message)
        app_state.current_page = "detail"

    async def _load_search(query: str) -> None:
        pkg_state.search_query = query
        await search_packages(pkg_state, api, query, 1)
        app_state.current_page = "packages"

    # --- Navigation ---
    def navigate(target: str) -> None:
        if target == "home":
            page.run_task(_load_home)
        elif target.startswith("detail:"):
            name = target.split(":", 1)[1]
            page.run_task(_load_detail, name)
        elif target.startswith("packages"):
            query = target.split(":", 1)[1] if ":" in target else ""
            page.run_task(_load_search, query)

    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state)

    def handle_pypi_filter_toggle() -> None:
        app_state.show_pypi_only = not app_state.show_pypi_only
        # Reload home data to apply the new filter
        pkg_state.home_data = None
        page.run_task(_load_home)

    def handle_search(query: str = "") -> None:
        navigate(f"packages:{query}")

    def handle_copy(text: str) -> None:
        page.run_task(ft.Clipboard().set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    # --- Context ---
    ctx_value = AppContextValue(
        state=app_state,
        api=api,
        navigate=navigate,
        toggle_theme=handle_theme_toggle,
        toggle_pypi_filter=handle_pypi_filter_toggle,
        search=handle_search,
        copy_to_clipboard=handle_copy,
    )

    # --- Initial load + render ---
    page.run_task(_load_home)
    page.render_views(App, ctx_value, app_state)


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
    )
