"""Root App component — returns ft.View with appbar, drawer, and page content.

Used with page.render_views(App, ctx_value).
"""

import flet as ft

from src.presentation.components.common.header import AppHeader
from src.presentation.pages.page_content import PageContent
from src.presentation.state_management.app_context import AppContextValue, AppCtx
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.colors import FLET_PINK


@ft.component
def App(ctx_value: AppContextValue, state: AppState) -> ft.View:
    """state is passed as @ft.observable arg so Flet re-renders when it changes."""
    view_ref = ft.use_ref()

    def open_drawer() -> None:
        if view_ref.current:
            ref = view_ref.current
            if ref.page:
                ref.page.run_task(ref.show_drawer)

    # Drawer (mobile)
    def on_drawer_change(e: ft.ControlEvent) -> None:
        index = e.control.selected_index
        if index == 0:  # Developer Guide
            ctx_value.navigate("guide")
        elif index == 1:  # Support & Contribute
            ctx_value.navigate("contribute")

    drawer = ft.NavigationDrawer(
        on_change=on_drawer_change,
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
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=16, top=20, right=16, bottom=10),
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            ft.NavigationDrawerDestination(label="Developer Guide", icon=ft.Icons.MENU_BOOK),
            ft.NavigationDrawerDestination(
                label="Support & Contribute", icon=ft.Icons.FAVORITE_OUTLINE
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Switch(
                            value=not state.show_pypi_only,
                            on_change=lambda _: ctx_value.toggle_pypi_filter(),
                            active_color=FLET_PINK,
                        ),
                        ft.Text(
                            "Show GitHub-only packages",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=16, top=4, right=16, bottom=4),
            ),
        ],
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        selected_index=-1,
    )

    # Content wrapped in context provider
    content = AppCtx(
        ctx_value,
        lambda: [
            ft.Column(
                controls=[
                    AppHeader(
                        on_theme_toggle=ctx_value.toggle_theme,
                        on_open_drawer=open_drawer,
                        on_navigate_home=lambda: ctx_value.navigate("home"),
                        on_search=ctx_value.search if state.current_page == "packages" else None,
                        on_toggle_pypi_filter=ctx_value.toggle_pypi_filter,
                        on_navigate_guide=lambda: ctx_value.navigate("guide"),
                        on_navigate_contribute=lambda: ctx_value.navigate("contribute"),
                        is_dark=state.is_dark,
                        show_logo=state.current_page != "home",
                        show_pypi_only=state.show_pypi_only,
                        search_query=state.packages.search_query,
                    ),
                    ft.Container(
                        content=PageContent(),
                        key=f"page_{state.current_page}",
                        expand=True,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        ],
    )

    view = ft.View(
        controls=content,
        drawer=drawer,
        padding=0,
        spacing=0,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        services=[ft.SharedPreferences(), ft.UrlLauncher()],
    )

    view_ref.current = view
    return view
