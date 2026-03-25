"""Page content router — reads current_page from context and renders the right page."""

import flet as ft

from src.domain.entities.package import Package
from src.presentation.pages.home.home_page import HomePage
from src.presentation.pages.package_detail.package_detail_page import PackageDetailPage
from src.presentation.pages.packages.packages_page import PackagesPage
from src.presentation.state_management.app_context import AppCtx


@ft.component
def PageContent() -> ft.Control:
    ctx = ft.use_context(AppCtx)
    state = ctx.state
    pkg_state = state.packages

    def handle_package_click(pkg: object) -> None:
        if isinstance(pkg, Package):
            ctx.navigate(f"detail:{pkg.pypi_name or pkg.name}")

    if state.current_page == "detail":
        return PackageDetailPage(
            state=pkg_state,
            user=state.user,
            api=ctx.api,
            package_name=state.detail_package_name,
            on_copy=ctx.copy_to_clipboard,
            on_back=lambda: ctx.navigate("home"),
        )
    elif state.current_page == "packages":
        return PackagesPage(
            state=pkg_state,
            api=ctx.api,
            on_package_click=handle_package_click,
            on_copy=ctx.copy_to_clipboard,
        )
    else:
        return HomePage(
            state=pkg_state,
            api=ctx.api,
            on_search=ctx.search,
            on_package_click=handle_package_click,
            on_view_all=lambda: ctx.search(""),
        )
