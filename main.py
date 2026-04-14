"""Application entry point — Composition Root.

Uses page.render_views() with ft.create_context() for proper declarative navigation.
URL routing: /, /guide, /packages, /packages?q=query, /packages/package-name

Navigation flow (unidirectional):
  navigate(target) → NavigationService.push(url) → on_route_change → _handle_route → load data
"""

import logging
import threading

import flet as ft

from config import settings
from src.core.logger import configure_logging
from src.domain.entities.package import SortOption
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

configure_logging()


def _patch_session(session) -> None:
    """Patch Flet session internals for resilience.

    1. Gracefully handle events on controls replaced during re-render.
    2. Protect the updates scheduler from crashing on stale/unmounted controls.

    Accesses Flet internal _Session__index and __updates_scheduler (name-mangled).
    Pinned to Flet 0.84.x — verify on every Flet upgrade.
    """
    flet_version = getattr(ft, "__version__", "unknown")
    if not str(flet_version).startswith("0.84."):
        logging.warning(
            "Flet version %s detected — _patch_session is pinned to 0.84.x. "
            "Skipping patches. Verify compatibility before re-enabling.",
            flet_version,
        )
        return

    # --- Patch 1: safe event dispatch ---
    index = getattr(session, "_Session__index", None)
    if index is None:
        logging.warning(
            "Flet Session.__index not found — _patch_session skipped. "
            "Check compatibility with current Flet version."
        )
        return

    original_dispatch = session.dispatch_event

    async def safe_dispatch(control_id, event_name, event_data):
        control = index.get(control_id)
        if control is None:
            return
        try:
            await original_dispatch(control_id, event_name, event_data)
        except Exception:
            logging.debug("Ignored event on detached %s(%s)", type(control).__name__, control_id)

    session.dispatch_event = safe_dispatch

    # --- Patch 2: resilient updates scheduler ---
    # The default scheduler crashes on any non-CancelledError exception
    # (e.g. RuntimeError from stale/unmounted component.update()).
    # This kills ALL subsequent UI updates for the session.
    original_schedule_update = session.schedule_update

    def safe_schedule_update(control):
        original_schedule_update(control)
        # Restart scheduler if it crashed (task is done with exception)
        task = getattr(session, "_Session__updates_task", None)
        if task and task.done():
            logging.warning("Updates scheduler was dead — restarting")
            session.start_updates_scheduler()

    session.schedule_update = safe_schedule_update


# --- Shared singleton: one index/cache for all sessions ---
_shared_api = ApiService()
_shared_api_started = False
_startup_lock = threading.Lock()


def main(page: ft.Page) -> None:
    global _shared_api_started

    page.title = "Flet PKG - Package Discovery"
    page.theme = get_light_theme()
    page.dark_theme = get_dark_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.spacing = 0

    _patch_session(page.session)

    # --- Dependency wiring (per-session state, shared api) ---
    app_state = AppState()
    api = _shared_api
    pkg_state = app_state.packages
    nav = NavigationService(page)
    prefs = ft.SharedPreferences()
    url_launcher = ft.UrlLauncher()
    share = ft.Share()
    connectivity = ft.Connectivity()

    # --- Connectivity monitoring ---
    async def _check_connectivity() -> None:
        """Check current connectivity and update app_state.is_offline."""
        try:
            results = await connectivity.get_connectivity()
            was_offline = app_state.is_offline
            app_state.is_offline = all(r == ft.ConnectivityType.NONE for r in results)
            # If we came back online, reload current page data
            if was_offline and not app_state.is_offline:
                logging.info("Connectivity restored — reloading data")
                _handle_route(page.route)
        except Exception:
            logging.debug("Connectivity check failed — assuming offline")
            app_state.is_offline = True

    def _on_connectivity_change(e: ft.ConnectivityChangeEvent) -> None:
        """React to connectivity changes in real-time."""
        app_state.is_offline = all(r == ft.ConnectivityType.NONE for r in e.connectivity)
        if not app_state.is_offline:
            logging.info("Connectivity restored — starting tasks and reloading data")
            page.run_task(_start_api_and_load)

    connectivity.on_change = _on_connectivity_change

    # start_background_tasks is deferred to _initial_load (after connectivity check)

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
            val = int(per_page)
            if val in settings.get("PAGE_SIZE_OPTIONS", [10, 25, 50, 100]):
                pkg_state.per_page = val

    # --- Data loaders ---
    async def _load_home() -> None:
        app_state.current_page = "home"
        if pkg_state.home_data is None:
            await load_home_data(pkg_state, api, pypi_only=app_state.show_pypi_only)

    async def _load_detail(name: str) -> None:
        logging.debug("[NAV] _load_detail START: %s", name)
        app_state.detail_package_name = name
        pkg_state.detail_package = None
        pkg_state.error = ""
        app_state.current_page = "detail"
        await load_package_detail_by_name(pkg_state, api, name)
        logging.debug(
            "[NAV] _load_detail END: %s (pkg=%s, err=%s, loading=%s)",
            name,
            "OK" if pkg_state.detail_package else "None",
            pkg_state.error or "none",
            pkg_state.detail_loading,
        )
        # Force re-render via manual notify — safe alternative to setting same value
        # (setting same value is a no-op for @ft.observable __setattr__)
        pkg_state.notify()
        app_state.notify()

    async def _load_search(
        query: str = "",
        sort: str = SortOption.DEFAULT,
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
            logging.debug("[NAV] Route SKIPPED (dedup): %s", route)
            return

        r = parse_route(route)
        logging.debug("[NAV] Route → %s (page=%s)", route, r.page)

        if r.page == "home":
            page.run_task(_load_home)
        elif r.page == "guide":
            app_state.current_page = "guide"
        elif r.page == "contribute":
            app_state.current_page = "contribute"
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

    clipboard = ft.Clipboard()

    def handle_copy(text: str) -> None:
        page.run_task(clipboard.set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    async def _do_share_text(text: str, subject: str | None) -> None:
        await share.share_text(text=text, subject=subject)

    def handle_share_url(text: str, subject: str | None = None) -> None:
        """Open native share sheet (mobile) or fallback to clipboard.

        Args:
            text: The text/URL to share. Can be a plain URL or formatted text.
            subject: Optional subject (used by email apps on Android).
        """
        if page.platform.is_mobile():
            page.run_task(_do_share_text, text, subject)
        else:
            page.run_task(clipboard.set, text)
            page.show_dialog(ft.SnackBar(ft.Text("Copied to clipboard")))

    # Note: ApiService is a singleton shared across all sessions.
    # Do NOT close it on session disconnect — the re-index loop and
    # other sessions still need the httpx clients.

    # --- Reconnection handler ---
    def _on_reconnect(_e) -> None:
        """Reset navigation state and reprocess route on WebSocket reconnection.

        Flet clears pending_updates on disconnect, so UI patches may be lost.
        Re-handling the route forces a fresh data load and re-render.
        """
        logging.info("Client reconnected — resetting navigation state")
        nav.reset()
        _handle_route(page.route)

    # --- URL event handlers ---
    page.on_connect = _on_reconnect
    page.on_route_change = lambda e: _handle_route(e.route)

    # --- Context ---
    ctx_value = AppContextValue(
        state=app_state,
        api=api,
        navigate=handle_navigate,
        go_back=nav.go_back,
        toggle_theme=handle_theme_toggle,
        toggle_pypi_filter=handle_pypi_filter_toggle,
        search=handle_search,
        reload_packages=handle_reload_packages,
        copy_to_clipboard=handle_copy,
        share_url=handle_share_url,
    )

    # --- Initial load + render ---
    # Start background tasks + load route only when online.
    # Used both at startup and when connectivity is restored.
    async def _start_api_and_load() -> None:
        global _shared_api_started
        with _startup_lock:
            if not _shared_api_started:
                _shared_api_started = True
                await api.start_background_tasks()
        _handle_route(page.route)

    # Check connectivity first. If offline on mobile,
    # the OfflineScreen shows immediately without trying HTTP requests.
    async def _initial_load() -> None:
        await _check_connectivity()
        if not app_state.is_offline:
            await _start_api_and_load()

    page.render_views(App, ctx_value, app_state, [prefs, url_launcher, share, connectivity])
    page.run_task(_load_preferences)
    page.run_task(_initial_load)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
