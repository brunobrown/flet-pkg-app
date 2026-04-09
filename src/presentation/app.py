"""Root layout — shared View with drawer, appbar, and page content.

This is the main layout component of the application, equivalent to a shared
Scaffold in Flutter. It wraps all screens with a common structure: navigation
drawer, header (AppBar), page content area, and floating action button.

Used with page.render_views(App, ctx_value, app_state, services).
"""

import flet as ft

from config import settings
from src.presentation.components.common.header import AppHeader
from src.presentation.pages.page_content import PageContent
from src.presentation.state_management.app_context import AppContextValue, AppCtx
from src.presentation.state_management.global_state import AppState
from src.presentation.themes.colors import FLET_PINK
from src.services.ads_service import is_ads_supported


@ft.component
def App(ctx_value: AppContextValue, state: AppState, services: list | None = None) -> ft.View:
    """state is passed as @ft.observable arg so Flet re-renders when it changes."""
    view_ref = ft.use_ref()

    def open_drawer() -> None:
        if view_ref.current:
            ref = view_ref.current
            if ref.page:
                ref.page.run_task(ref.show_drawer)

    # Drawer (mobile)
    def _open_docs() -> None:
        ft.context.page.run_task(
            ft.UrlLauncher().launch_url,
            "https://brunobrown.github.io/flet-pkg-app/",
        )

    def _close_drawer() -> None:
        if view_ref.current and view_ref.current.page:
            view_ref.current.page.run_task(view_ref.current.close_drawer)

    def on_drawer_change(e: ft.ControlEvent) -> None:
        index = e.control.selected_index
        _close_drawer()
        if index == 0:  # Developer Guide
            ctx_value.navigate("guide")
        elif index == 1:  # Documentation
            _open_docs()
        elif index == 2:  # Support & Contribute
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
            ft.NavigationDrawerDestination(label="Documentation", icon=ft.Icons.ARTICLE_OUTLINED),
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
        ]
        + (
            [
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                # Footer links moved to drawer on mobile (hidden from footer near ads)
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url=settings.get("FOOTER_LINKS", {}).get("discord", ""),
                                tooltip="Discord",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CODE,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url=settings.get("FOOTER_LINKS", {}).get("github", ""),
                                tooltip="GitHub",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARTICLE_OUTLINED,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url=settings.get("FOOTER_LINKS", {}).get("blog", ""),
                                tooltip="Blog",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.SUPPORT,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url=settings.get("FOOTER_LINKS", {}).get("support", ""),
                                tooltip="Support",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                ),
                # Dynamic spacer: push BMC button to bottom of drawer
                ft.Container(
                    height=max(0, (ft.context.page.height or 800) - 500),
                ),
                ft.Container(
                    content=ft.Container(
                        content=ft.Image(
                            src="/icons/bmc-logo-no-background.png",
                            width=26,
                            height=26,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        width=48,
                        height=48,
                        bgcolor="#FFDD00",
                        border_radius=24,
                        alignment=ft.Alignment.CENTER,
                    ),
                    alignment=ft.Alignment.BOTTOM_RIGHT,
                    padding=ft.Padding(left=0, top=0, right=16, bottom=16),
                    on_click=lambda _: ft.context.page.run_task(
                        ft.UrlLauncher().launch_url,
                        "https://www.buymeacoffee.com/brunobrown",
                    ),
                ),
            ]
            if is_ads_supported()
            else []
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        selected_index=-1,
    )

    # Persistent bottom banner ad — created once, reused across renders (mobile only)
    def _create_bottom_banner():
        if not is_ads_supported():
            return None
        from flet_ads import BannerAd

        platform = ft.context.page.platform
        unit_id = (
            settings.get("ADS_BANNER", {}).get("ios", "")
            if platform == ft.PagePlatform.IOS
            else settings.get("ADS_BANNER", {}).get("android", "")
        )
        if not unit_id:
            return None
        import logging

        logger = logging.getLogger(__name__)
        return BannerAd(
            unit_id=unit_id,
            width=320,
            height=50,
            on_load=lambda e: logger.info("[ADS] Banner loaded OK"),
            on_error=lambda e: logger.warning("[ADS] Banner error: %s", e.data),
        )

    bottom_banner = ft.use_memo(_create_bottom_banner, [])

    # Bottom banner container (centered, visible on mobile only)
    banner_row = (
        ft.Container(
            content=bottom_banner,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
        )
        if bottom_banner
        else None
    )

    # Content wrapped in context provider.
    # SafeArea wraps only the header to avoid status bar overlap on mobile,
    # while keeping the scrollable page content unaffected.
    content = AppCtx(
        ctx_value,
        lambda: [
            ft.Column(
                controls=[
                    ft.SafeArea(
                        content=ft.Container(
                            content=AppHeader(
                                on_theme_toggle=ctx_value.toggle_theme,
                                on_open_drawer=open_drawer,
                                on_navigate_home=lambda: ctx_value.navigate("home"),
                                on_search=ctx_value.search
                                if state.current_page == "packages"
                                else None,
                                on_toggle_pypi_filter=ctx_value.toggle_pypi_filter,
                                on_navigate_guide=lambda: ctx_value.navigate("guide"),
                                on_navigate_contribute=lambda: ctx_value.navigate("contribute"),
                                is_dark=state.is_dark,
                                show_logo=state.current_page != "home",
                                show_pypi_only=state.show_pypi_only,
                                search_query=state.packages.search_query,
                            ),
                        ),
                        avoid_intrusions_bottom=False,
                    ),
                    ft.Container(
                        content=PageContent(),
                        key=f"page_{state.current_page}",
                        expand=True,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
                    ),
                ]
                + ([banner_row] if banner_row else []),
                spacing=0,
                expand=True,
            )
        ],
    )

    # FAB hidden on native mobile — BMC is always in the drawer there.
    show_fab = not is_ads_supported()

    def _open_bmc(_e: ft.ControlEvent) -> None:
        _e.page.run_task(ft.UrlLauncher().launch_url, "https://www.buymeacoffee.com/brunobrown")

    bmc_button = (
        ft.FloatingActionButton(
            content=ft.Image(
                src="/icons/bmc-logo-no-background.png",
                width=28,
                height=28,
                fit=ft.BoxFit.CONTAIN,
            ),
            bgcolor="#FFDD00",
            shape=ft.CircleBorder(),
            mini=True,
            tooltip="Buy me a coffee",
            on_click=_open_bmc,
        )
        if show_fab
        else None
    )

    async def _on_confirm_pop(e: ft.ControlEvent) -> None:
        """Handle Android back button: navigate back or allow exit at root."""
        previous = ctx_value.go_back()
        if previous is not None:
            # Had history — cancel the pop (stay in app, navigate back)
            await e.control.confirm_pop(False)
        else:
            # No history (at root) — allow default behavior (minimize/exit)
            await e.control.confirm_pop(True)

    view = ft.View(
        controls=content,
        drawer=drawer,
        floating_action_button=bmc_button,
        padding=0,
        spacing=0,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        services=services or [],
        can_pop=False,
        on_confirm_pop=_on_confirm_pop,
    )

    view_ref.current = view
    return view
