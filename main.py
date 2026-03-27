"""Application entry point — Composition Root.

Uses page.render_views() with ft.create_context() for proper declarative navigation.
URL routing: /, /packages, /packages?q=query, /packages/package-name

Navigation flow (unidirectional):
  navigate(target) → _push(url) → browser URL changes → on_route_change → _handle_route → load data
"""

import logging
import urllib.parse

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


def _parse_route(route: str) -> tuple[str, dict[str, str]]:
    """Parse a URL route into (path, query_params)."""
    parsed = urllib.parse.urlparse(route)
    path = parsed.path.strip("/")
    params = dict(urllib.parse.parse_qsl(parsed.query))
    return path, params


_TYPE_MAP = {"services": "Services", "ui-controls": "UI Controls", "python": "Python Package"}
_TYPE_MAP_REVERSE = {v: k for k, v in _TYPE_MAP.items()}


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

    page.run_task(api.start_background_tasks)

    # --- Data loaders (called ONLY from _handle_route) ---
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
        page_num: int = 1,
    ) -> None:
        pkg_state.search_query = query
        pkg_state.sort_by = sort
        pkg_state.filter_type = filter_type
        pkg_state.filter_official = official
        pkg_state.page_number = page_num
        app_state.current_page = "packages"
        await search_packages(pkg_state, api, query, page_num, pypi_only=app_state.show_pypi_only)

    # --- Route handling (single source of truth for data loading) ---
    _last_handled_route: str = ""

    def _handle_route(route: str) -> None:
        """Parse URL route and trigger the appropriate data load.

        Skips reload if the route was already handled (avoids double-load when
        handle_reload_packages does _load_search + _push in sequence).
        """
        nonlocal _last_handled_route
        if route == _last_handled_route:
            return
        _last_handled_route = route

        path, params = _parse_route(route)

        if path == "" or path == "/":
            page.run_task(_load_home)
        elif path == "packages":
            query = params.get("q", "")
            sort = params.get("sort", "default ranking")
            filter_type = _TYPE_MAP.get(params.get("type", ""))
            official = params.get("official", "") == "true"
            page_num = int(params.get("page", "1"))
            page.run_task(_load_search, query, sort, filter_type, official, page_num)
        elif path.startswith("packages/"):
            name = path.split("/", 1)[1]
            if name:
                page.run_task(_load_detail, name)
            else:
                page.run_task(_load_search)
        else:
            page.run_task(_load_home)

    # --- Navigation: build URL and push (triggers on_route_change → _handle_route) ---
    def _push(route: str) -> None:
        page.run_task(page.push_route, route)

    def _build_packages_url(
        query: str = "",
        sort: str = "default ranking",
        filter_type: str | None = None,
        official: bool = False,
        page_num: int = 1,
    ) -> str:
        """Build /packages URL from explicit params."""
        qparams: dict[str, str] = {}
        if query:
            qparams["q"] = query
        if sort and sort != "default ranking":
            qparams["sort"] = sort
        if filter_type:
            type_key = _TYPE_MAP_REVERSE.get(filter_type, "")
            if type_key:
                qparams["type"] = type_key
        if official:
            qparams["official"] = "true"
        if page_num > 1:
            qparams["page"] = str(page_num)
        qs = f"?{urllib.parse.urlencode(qparams)}" if qparams else ""
        return f"/packages{qs}"

    def navigate(target: str) -> None:
        """Navigate by pushing a new URL. on_route_change handles data loading.

        target formats:
            "home"                                  -> /
            "packages:query"                        -> /packages?q=query
            "packages"                              -> /packages
            "packages_filtered:sort:type:official"  -> /packages?sort=X&type=Y&official=true
            "detail:name"                           -> /packages/name
        """
        if target == "home":
            _push("/")
        elif target.startswith("detail:"):
            name = target.split(":", 1)[1]
            _push(f"/packages/{name}")
        elif target.startswith("packages_filtered:"):
            parts = target.split(":", 3)
            sort = parts[1] if len(parts) > 1 else "default ranking"
            type_key = parts[2] if len(parts) > 2 else ""
            official = parts[3] if len(parts) > 3 else ""
            qparams: dict[str, str] = {}
            if sort and sort != "default ranking":
                qparams["sort"] = sort
            if type_key:
                qparams["type"] = type_key
            if official == "true":
                qparams["official"] = "true"
            qs = f"?{urllib.parse.urlencode(qparams)}" if qparams else ""
            _push(f"/packages{qs}")
        elif target.startswith("packages"):
            query = target.split(":", 1)[1] if ":" in target else ""
            if query:
                _push(f"/packages?q={urllib.parse.quote(query)}")
            else:
                _push("/packages")

    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state)

    def handle_pypi_filter_toggle() -> None:
        app_state.show_pypi_only = not app_state.show_pypi_only
        if app_state.current_page == "packages":
            # Reload directly — pypi_only is not in the URL, so push_route
            # would get deduplicated by Flet's before_event (same URL).
            page.run_task(
                _load_search,
                pkg_state.search_query,
                pkg_state.sort_by,
                pkg_state.filter_type,
                pkg_state.filter_official,
                pkg_state.page_number,
            )
        else:
            pkg_state.home_data = None
            page.run_task(_load_home)

    def handle_search(query: str = "") -> None:
        navigate(f"packages:{query}")

    def handle_reload_packages() -> None:
        """Reload search with current state params and sync browser URL.

        Loads data directly (not via push_route) to avoid Flet's route
        deduplication in before_event(). Updates _last_handled_route before
        pushing so on_route_change skips the redundant load.
        """
        nonlocal _last_handled_route
        url = _build_packages_url(
            query=pkg_state.search_query,
            sort=pkg_state.sort_by,
            filter_type=pkg_state.filter_type,
            official=pkg_state.filter_official,
            page_num=pkg_state.page_number,
        )
        _last_handled_route = url
        page.run_task(
            _load_search,
            pkg_state.search_query,
            pkg_state.sort_by,
            pkg_state.filter_type,
            pkg_state.filter_official,
            pkg_state.page_number,
        )
        _push(url)

    def handle_copy(text: str) -> None:
        page.run_task(ft.Clipboard().set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    # --- URL event handlers ---
    def on_route_change(_e: ft.RouteChangeEvent) -> None:
        _handle_route(_e.route)

    def on_view_pop(_e: ft.ViewPopEvent) -> None:
        _handle_route(page.route)

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    # --- Context ---
    ctx_value = AppContextValue(
        state=app_state,
        api=api,
        navigate=navigate,
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
