"""Application entry point — Composition Root.

Uses page.render() for declarative rendering.
Header is a @ft.component inside AppRoot (recreated each render, never orphaned).
Navigation pre-loads data via page.run_task, then changes route.
Pages read state directly — no dependency on use_effect for data loading.
"""

import flet as ft

from src.domain.entities.package import Package
from src.presentation.components.common.header import AppHeader
from src.presentation.hooks.use_packages import (
    load_home_data,
    load_package_detail_by_name,
    search_packages,
)
from src.presentation.hooks.use_theme import toggle_theme_mode
from src.presentation.navigation.app_router import build_packages_route, parse_route
from src.presentation.pages.home.home_page import HomePage
from src.presentation.pages.package_detail.package_detail_page import PackageDetailPage
from src.presentation.pages.packages.packages_page import PackagesPage
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.app_theme import get_dark_theme, get_light_theme
from src.presentation.themes.colors import DARK_BG
from src.services.api_service import ApiService


def _patch_session_dispatch(session) -> None:
    """Patch session.dispatch_event to skip orphaned controls (no parent chain).

    Prevents SESSION_CRASHED when a control receives an event after being
    removed from the page tree during a re-render.
    """
    import logging

    original_dispatch = session.dispatch_event

    async def safe_dispatch(control_id, event_name, event_data):
        control = session._Session__index.get(control_id)
        if control and control.parent is None:
            logging.debug("Skipping event on orphaned control %s", control_id)
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

    # Prevent crash on orphaned control events during navigation
    _patch_session_dispatch(page.session)

    # --- Dependency wiring ---
    app_state = AppState()
    api = ApiService()
    pkg_state = app_state.packages

    # --- Callbacks ---
    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state)

    def open_drawer() -> None:
        page.run_task(page.show_drawer)

    # --- Drawer (mobile) ---
    page.views[0].drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src="/images/flet.svg", width=28, height=28, fit=ft.BoxFit.CONTAIN
                        ),
                        ft.Text(
                            "Flet PKG",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=16, top=20, right=16, bottom=10),
            ),
            ft.Divider(color="#354457"),
            ft.NavigationDrawerDestination(
                label="Introduction",
                icon=ft.Icons.MENU_BOOK,
            ),
            ft.NavigationDrawerDestination(
                label="API Reference",
                icon=ft.Icons.CODE,
            ),
            ft.NavigationDrawerDestination(
                label="About Flet PKG",
                icon=ft.Icons.INFO_OUTLINE,
            ),
        ],
        bgcolor="#14253A",
        selected_index=-1,
    )

    # --- Data loading (called from navigate, runs in Flet's event loop) ---
    async def _load_home_async() -> None:
        if pkg_state.home_data is None:
            await load_home_data(pkg_state, api)
        app_state.current_route = "/"

    async def _load_detail_async(name: str) -> None:
        app_state.detail_package_name = name
        pkg_state.detail_package = None
        await load_package_detail_by_name(pkg_state, api, name)
        app_state.current_route = f"/packages/{name}"

    async def _load_search_async(query: str) -> None:
        pkg_state.search_query = query
        await search_packages(pkg_state, api, query, 1)
        app_state.current_route = build_packages_route(query)

    # --- Navigation ---
    def navigate(route: str) -> None:
        nav_parsed = parse_route(route)
        if nav_parsed.is_home:
            page.run_task(_load_home_async)
        elif nav_parsed.is_package_detail:
            page.run_task(_load_detail_async, nav_parsed.package_name)
        elif nav_parsed.is_packages:
            page.run_task(_load_search_async, nav_parsed.search_query)

    def handle_search(query: str = "") -> None:
        navigate(build_packages_route(query))

    def handle_package_click(pkg: object) -> None:
        if isinstance(pkg, Package):
            navigate(f"/packages/{pkg.pypi_name or pkg.name}")

    def handle_copy(text: str) -> None:
        page.run_task(ft.Clipboard().set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    # --- Initial data load ---
    if page.route and page.route != "/":
        parsed = parse_route(page.route)
        if parsed.is_package_detail:
            app_state.detail_package_name = parsed.package_name
            app_state.current_route = page.route
        elif parsed.is_packages:
            pkg_state.search_query = parsed.search_query
            app_state.current_route = page.route
    else:
        # Pre-load home data
        page.run_task(_load_home_async)

    # --- Root component ---
    @ft.component
    def AppRoot(state: AppState) -> list[ft.Control]:
        route_parsed = parse_route(state.current_route)

        if route_parsed.is_package_detail:
            page_content = PackageDetailPage(
                state=state.packages,
                user=state.user,
                api=api,
                package_name=state.detail_package_name,
                on_copy=handle_copy,
                on_back=lambda: navigate("/"),
            )
        elif route_parsed.is_packages:
            page_content = PackagesPage(
                state=state.packages,
                api=api,
                on_package_click=handle_package_click,
                on_copy=handle_copy,
            )
        else:
            page_content = HomePage(
                state=state.packages,
                api=api,
                on_search=handle_search,
                on_package_click=handle_package_click,
                on_view_all=lambda: handle_search(""),
            )

        return [
            ft.Column(
                controls=[
                    AppHeader(
                        on_theme_toggle=handle_theme_toggle,
                        on_open_drawer=open_drawer,
                        on_navigate_home=lambda: navigate("/"),
                        on_search=handle_search if route_parsed.is_packages else None,
                        is_dark=state.is_dark,
                        show_logo=not route_parsed.is_home,
                        search_query=state.packages.search_query,
                    ),
                    ft.Container(
                        content=page_content,
                        expand=True,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        ]

    page.render(AppRoot, app_state)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")
