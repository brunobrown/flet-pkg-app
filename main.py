"""Application entry point — Composition Root.

Uses page.render() for declarative rendering.
Observable state passed as component args triggers re-renders.
"""

import asyncio

import flet as ft

from src.domain.entities.package import Package
from src.presentation.components.common.header import AppHeader
from src.presentation.hooks.use_packages import load_package_detail_by_name, search_packages
from src.presentation.hooks.use_theme import toggle_theme_mode
from src.presentation.navigation.app_router import build_packages_route, parse_route
from src.presentation.pages.home.home_page import HomePage
from src.presentation.pages.package_detail.package_detail_page import PackageDetailPage
from src.presentation.pages.packages.packages_page import PackagesPage
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.app_theme import get_dark_theme, get_light_theme
from src.presentation.themes.colors import DARK_BG, LIGHT_BG
from src.services.api_service import ApiService


def main(page: ft.Page) -> None:
    # --- Page configuration ---
    page.title = "Flet PKG - Package Discovery"
    page.theme = get_light_theme()
    page.dark_theme = get_dark_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = DARK_BG
    page.padding = 0
    page.spacing = 0

    # --- Dependency wiring ---
    app_state = AppState()
    api = ApiService()
    pkg_state = app_state.packages

    # --- Navigation via state ---
    def navigate(route: str) -> None:
        """Update state route (triggers re-render) and sync browser URL."""
        parsed = parse_route(route)
        app_state.current_route = route

        if parsed.is_package_detail:
            app_state.detail_package_name = parsed.package_name
            asyncio.ensure_future(load_package_detail_by_name(pkg_state, api, parsed.package_name))
        elif parsed.is_packages:
            pkg_state.search_query = parsed.search_query
            asyncio.ensure_future(search_packages(pkg_state, api, parsed.search_query, 1))

        asyncio.create_task(page.push_route(route))

    def handle_search(query: str = "") -> None:
        pkg_state.search_query = query
        navigate(build_packages_route(query))

    def handle_package_click(pkg: object) -> None:
        if isinstance(pkg, Package):
            navigate(f"/packages/{pkg.pypi_name or pkg.name}")

    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state.theme)

    def handle_copy(text: str) -> None:
        page.set_clipboard(text)
        page.open(ft.SnackBar(content=ft.Text(f"Copied: {text}"), duration=2000))

    def handle_view_all() -> None:
        handle_search("")

    # --- Sync browser navigation → state ---
    def on_route_change() -> None:
        if page.route != app_state.current_route:
            parsed = parse_route(page.route)
            app_state.current_route = page.route
            if parsed.is_package_detail:
                app_state.detail_package_name = parsed.package_name
                asyncio.ensure_future(
                    load_package_detail_by_name(pkg_state, api, parsed.package_name)
                )
            elif parsed.is_packages:
                pkg_state.search_query = parsed.search_query
                asyncio.ensure_future(search_packages(pkg_state, api, parsed.search_query, 1))

    page.on_route_change = on_route_change

    # --- Root component ---
    # IMPORTANT: app_state is passed as argument so Flet's renderer
    # tracks its @ft.observable fields and re-renders on changes.
    @ft.component
    def AppRoot(state: AppState) -> list[ft.Control]:
        parsed = parse_route(state.current_route)
        is_dark = state.theme.is_dark
        bg = DARK_BG if is_dark else LIGHT_BG

        # Determine which page to show
        if parsed.is_package_detail:
            page_content = PackageDetailPage(
                state=state.packages,
                user=state.user,
                api=api,
                package_name=state.detail_package_name,
                on_copy=handle_copy,
                on_back=lambda: navigate(build_packages_route()),
            )
            show_header = True
        elif parsed.is_packages:
            page_content = PackagesPage(
                state=state.packages,
                api=api,
                on_package_click=handle_package_click,
                on_copy=handle_copy,
            )
            show_header = True
        else:
            page_content = HomePage(
                state=state.packages,
                api=api,
                on_search=handle_search,
                on_package_click=handle_package_click,
                on_view_all=handle_view_all,
                on_theme_toggle=handle_theme_toggle,
            )
            show_header = False

        # Build layout
        controls: list[ft.Control] = []
        if show_header:
            controls.append(
                AppHeader(
                    on_search=handle_search,
                    on_theme_toggle=handle_theme_toggle,
                    on_navigate_home=lambda: navigate("/"),
                    search_query=state.packages.search_query,
                )
            )
        controls.append(ft.Container(content=page_content, expand=True, bgcolor=bg))

        return [
            ft.Container(
                content=ft.Column(controls=controls, spacing=0, expand=True),
                expand=True,
                bgcolor=bg,
            )
        ]

    # --- Start ---
    page.render(AppRoot, app_state)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)
