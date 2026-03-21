import flet as ft

from src.core.constants import PACKAGES_PER_PAGE, SORT_OPTIONS
from src.presentation.components.common.loading import ErrorMessage, LoadingIndicator
from src.presentation.components.common.package_card import PackageCard
from src.presentation.components.common.pagination import Pagination
from src.presentation.components.sections.sidebar_filters import SidebarFilters
from src.presentation.state_management.global_state import PackagesState
from src.presentation.themes.colors import DARK_ACCENT, DARK_CARD
from src.services.api_service import ApiService


@ft.component
def PackagesPage(
    state: PackagesState,
    api: ApiService,
    on_package_click: object,
    on_copy: object,
) -> ft.Control:
    # State-driven: data loaded by navigate() in main.py
    # Filters are local UI state
    filter_ui, set_filter_ui = ft.use_state(False)
    filter_services, set_filter_services = ft.use_state(False)
    filter_official, set_filter_official = ft.use_state(False)
    filter_screenshot, set_filter_screenshot = ft.use_state(False)

    def on_ui_change(val: bool) -> None:
        set_filter_ui(val)

    def on_services_change(val: bool) -> None:
        set_filter_services(val)

    def on_official_change(val: bool) -> None:
        set_filter_official(val)

    def on_screenshot_change(val: bool) -> None:
        set_filter_screenshot(val)

    # Build package list from state
    package_list: list[ft.Control] = []
    if state.is_loading:
        package_list.append(LoadingIndicator("Searching packages..."))
    elif state.error:
        package_list.append(ErrorMessage(state.error))
    elif not state.packages:
        package_list.append(
            ft.Container(
                content=ft.Text("No packages found", color="#8A92A2", size=16),
                padding=40,
                alignment=ft.Alignment.CENTER,
            )
        )
    else:
        for pkg in state.packages:
            package_list.append(PackageCard(pkg, on_click=on_package_click, on_copy=on_copy))

    sort_items = [ft.DropdownOption(text=s, key=s) for s in SORT_OPTIONS]

    return ft.Row(
        controls=[
            # Sidebar
            ft.Container(
                content=SidebarFilters(
                    filter_ui=filter_ui,
                    filter_services=filter_services,
                    filter_official=filter_official,
                    filter_screenshot=filter_screenshot,
                    on_filter_ui=on_ui_change,
                    on_filter_services=on_services_change,
                    on_filter_official=on_official_change,
                    on_filter_screenshot=on_screenshot_change,
                ),
                padding=ft.Padding(left=20, top=20, right=0, bottom=20),
            ),
            # Main content
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                "RESULTS",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    str(state.total_count),
                                                    size=12,
                                                    color=ft.Colors.WHITE,
                                                ),
                                                bgcolor=DARK_ACCENT,
                                                border_radius=4,
                                                padding=ft.Padding(
                                                    left=6, top=2, right=6, bottom=2
                                                ),
                                            ),
                                            ft.Text("packages", size=14, color="#8A92A2"),
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text("SORT BY", size=12, color="#8A92A2"),
                                            ft.Dropdown(
                                                value=state.sort_by,
                                                options=sort_items,
                                                on_select=lambda e: None,
                                                width=180,
                                                height=36,
                                                text_size=12,
                                                border_color=DARK_ACCENT,
                                                color=DARK_ACCENT,
                                                bgcolor=DARK_CARD,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.Padding(left=0, top=20, right=20, bottom=10),
                        ),
                        *package_list,
                        Pagination(
                            current_page=state.current_page,
                            total_items=state.total_count,
                            per_page=PACKAGES_PER_PAGE,
                            on_page_change=lambda p: None,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                expand=True,
                padding=ft.Padding(left=20, top=0, right=0, bottom=0),
            ),
        ],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=0,
    )
