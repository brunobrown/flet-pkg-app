"""Page content router — reads current_page from context and renders the right page."""

import flet as ft

from src.domain.entities.package import Package
from src.presentation.pages.contribute.contribute_page import ContributePage
from src.presentation.pages.guide.developer_guide_page import DeveloperGuidePage
from src.presentation.pages.home.home_page import HomePage
from src.presentation.pages.package_detail.package_detail_page import PackageDetailPage
from src.presentation.pages.packages.packages_page import PackagesPage
from src.presentation.state_management.app_context import AppCtx


@ft.component
def PageContent() -> ft.Control:
    ctx = ft.use_context(AppCtx)
    if ctx is None:
        return ft.Container()
    state = ctx.state
    pkg_state = state.packages

    def handle_package_click(pkg: object) -> None:
        if isinstance(pkg, Package):
            name = pkg.pypi_name or pkg.name
            ctx.navigate(f"detail:{name}")

    if state.current_page == "guide":
        return DeveloperGuidePage()
    elif state.current_page == "contribute":
        return ContributePage()
    elif state.current_page == "detail":
        return PackageDetailPage(
            state=pkg_state,
            user=state.user,
            api=ctx.api,
            package_name=state.detail_package_name,
            on_copy=ctx.copy_to_clipboard,
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
            on_navigate=ctx.navigate,
        )
