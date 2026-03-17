import flet as ft

from src.presentation.components.common.loading import ErrorMessage, LoadingIndicator
from src.presentation.components.common.search_bar import HeroSearchBar
from src.presentation.components.sections.package_section import PackageSection
from src.presentation.hooks.use_packages import load_home_data
from src.presentation.state_management.global_state import PackagesState
from src.services.api_service import ApiService


@ft.component
def HomePage(
    state: PackagesState,
    api: ApiService,
    on_search: object,
    on_package_click: object,
    on_view_all: object,
    on_theme_toggle: object = None,
) -> ft.Control:
    loading, set_loading = ft.use_state(True)
    error, set_error = ft.use_state("")
    retry_count, set_retry_count = ft.use_state(0)

    async def _load_home():
        set_loading(True)
        set_error("")
        try:
            await load_home_data(state, api)
        except Exception as e:
            set_error(str(e))
        set_loading(False)

    ft.use_effect(_load_home, dependencies=[retry_count])

    if loading:
        return ft.Column(
            controls=[
                HeroSearchBar(on_search, on_theme_toggle=on_theme_toggle),
                LoadingIndicator("Loading packages..."),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    if error:
        return ft.Column(
            controls=[
                HeroSearchBar(on_search, on_theme_toggle=on_theme_toggle),
                ErrorMessage(error, on_retry=lambda: set_retry_count(lambda v: v + 1)),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    sections: list[ft.Control] = [HeroSearchBar(on_search, on_theme_toggle=on_theme_toggle)]

    if state.home_data:
        hd = state.home_data

        if hd.official_packages:
            sections.append(
                PackageSection(
                    title="Official Flet Extensions",
                    description="Official extension packages maintained by the Flet team",
                    packages=hd.official_packages,
                    on_package_click=on_package_click,
                    on_view_all=on_view_all,
                    max_cards=4,
                    cols_per_row=4,
                )
            )

        if hd.trending_packages:
            sections.append(
                PackageSection(
                    title="Trending packages",
                    description="Top trending packages in the last 30 days",
                    packages=hd.trending_packages,
                    on_package_click=on_package_click,
                    on_view_all=on_view_all,
                )
            )

        if hd.service_packages:
            sections.append(
                PackageSection(
                    title="Flutter Extensions for Flet (Services)",
                    description=(
                        "Extensions that wrap Flutter packages as Flet services "
                        "- SDKs, background services, platform APIs"
                    ),
                    packages=hd.service_packages,
                    on_package_click=on_package_click,
                    on_view_all=on_view_all,
                )
            )

        if hd.ui_control_packages:
            sections.append(
                PackageSection(
                    title="Flutter Extensions for Flet (UI Controls)",
                    description=(
                        "Extensions that wrap Flutter packages as Flet UI controls "
                        "- visual widgets that render on screen"
                    ),
                    packages=hd.ui_control_packages,
                    on_package_click=on_package_click,
                    on_view_all=on_view_all,
                )
            )

        if hd.python_packages:
            sections.append(
                PackageSection(
                    title="Top Python Packages for Flet",
                    description=(
                        "Python packages that depend on or are commonly used "
                        "with Flet, but are not Flutter extensions"
                    ),
                    packages=hd.python_packages,
                    on_package_click=on_package_click,
                    on_view_all=on_view_all,
                )
            )

    return ft.Column(
        controls=sections,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )
