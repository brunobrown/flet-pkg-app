"""Application entry point — Composition Root.

Uses page.render() for declarative rendering.
Observable state passed as component args triggers re-renders.
Async data loading uses ft.use_effect() inside components.
Navigation changes observable state → triggers re-render of AppRoot.
URL sync uses asyncio.create_task (NOT page.run_task) to preserve ContextVar.
"""

import asyncio

import flet as ft

from src.domain.entities.package import Package
from src.presentation.components.common.header import AppHeader
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

    # --- Navigation: change state + sync browser URL ---
    _navigating = False

    def navigate(route: str) -> None:
        nonlocal _navigating
        if _navigating:
            return
        _navigating = True

        nav_parsed = parse_route(route)
        if nav_parsed.is_package_detail:
            app_state.detail_package_name = nav_parsed.package_name
        elif nav_parsed.is_packages:
            pkg_state.search_query = nav_parsed.search_query
        # Triggers AppRoot re-render via observable
        app_state.current_route = route
        # Sync browser URL — asyncio.create_task copies ContextVar (Python 3.12+)
        asyncio.create_task(page.push_route(route))

        _navigating = False

    def handle_search(query: str = "") -> None:
        navigate(build_packages_route(query))

    def handle_package_click(pkg: object) -> None:
        if isinstance(pkg, Package):
            navigate(f"/packages/{pkg.pypi_name or pkg.name}")

    def handle_theme_toggle() -> None:
        toggle_theme_mode(page, app_state.theme)

    def handle_copy(text: str) -> None:
        page.run_task(ft.Clipboard().set, text)
        page.show_dialog(ft.SnackBar(ft.Text(f"Copied: {text}")))

    # --- Browser back/forward → sync state ---
    def on_route_change() -> None:
        if page.route != app_state.current_route:
            navigate(page.route)

    page.on_route_change = on_route_change

    # --- Sync initial route from browser URL ---
    if page.route and page.route != "/":
        parsed = parse_route(page.route)
        if parsed.is_package_detail:
            app_state.detail_package_name = parsed.package_name
        elif parsed.is_packages:
            pkg_state.search_query = parsed.search_query
        app_state.current_route = page.route

    # --- Root component ---
    @ft.component
    def AppRoot(state: AppState) -> list[ft.Control]:
        parsed = parse_route(state.current_route)
        is_dark = state.theme.is_dark
        bg = DARK_BG if is_dark else LIGHT_BG

        if parsed.is_package_detail:
            page_content = PackageDetailPage(
                state=state.packages,
                user=state.user,
                api=api,
                package_name=state.detail_package_name,
                on_copy=handle_copy,
                on_back=lambda: navigate("/"),
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
                on_view_all=lambda: handle_search(""),
                on_theme_toggle=handle_theme_toggle,
            )
            show_header = False

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

    page.render(AppRoot, app_state)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")
