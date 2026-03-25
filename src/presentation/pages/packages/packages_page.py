"""Packages list page — slide-in filter panel like detail page sidebar."""

import flet as ft

from config import settings
from src.presentation.components.common.footer import AppFooter
from src.presentation.components.common.loading import ErrorMessage, LoadingIndicator
from src.presentation.components.common.package_card import PackageCard
from src.presentation.components.common.pagination import Pagination
from src.presentation.components.sections.sidebar_filters import SidebarFilters
from src.presentation.state_management.global_state import PackagesState
from src.presentation.themes.colors import FLET_PINK
from src.services.api_service import ApiService


@ft.component
def PackagesPage(
    state: PackagesState,
    api: ApiService,
    on_package_click: object,
    on_copy: object,
) -> ft.Control:
    filter_ui, set_filter_ui = ft.use_state(False)
    filter_services, set_filter_services = ft.use_state(False)
    filter_official, set_filter_official = ft.use_state(False)
    filter_screenshot, set_filter_screenshot = ft.use_state(False)
    filters_open, set_filters_open = ft.use_state(False)

    # Build package list from state
    package_list: list[ft.Control] = []
    if state.is_loading:
        package_list.append(LoadingIndicator("Searching packages..."))
    elif state.error:
        package_list.append(ErrorMessage(state.error))
    elif not state.packages:
        package_list.append(
            ft.Container(
                content=ft.Text("No packages found", color=ft.Colors.ON_SURFACE_VARIANT, size=16),
                padding=40,
                alignment=ft.Alignment.CENTER,
            )
        )
    else:
        for pkg in state.packages:
            package_list.append(PackageCard(pkg, on_click=on_package_click, on_copy=on_copy))

    sort_items = [ft.DropdownOption(text=s, key=s) for s in settings.SORT_OPTIONS]

    # --- Filter sidebar content ---
    filter_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Filters", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=18,
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        on_click=lambda _: set_filters_open(False),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            SidebarFilters(
                filter_ui=filter_ui,
                filter_services=filter_services,
                filter_official=filter_official,
                filter_screenshot=filter_screenshot,
                on_filter_ui=lambda v: set_filter_ui(v),
                on_filter_services=lambda v: set_filter_services(v),
                on_filter_official=lambda v: set_filter_official(v),
                on_filter_screenshot=lambda v: set_filter_screenshot(v),
            ),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    # --- Slide-in filter panel ---
    filter_panel = ft.Container(
        content=filter_content,
        width=260,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        padding=16,
        border_radius=ft.BorderRadius(top_left=12, bottom_left=12, top_right=0, bottom_right=0),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(-2, 0),
        ),
        right=0,
        top=0,
        bottom=0,
        offset=ft.Offset(0, 0) if filters_open else ft.Offset(1, 0),
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Toggle tab (vertical strip on right edge) ---
    toggle_tab = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.CHEVRON_LEFT if filters_open else ft.Icons.FILTER_LIST,
                    size=18,
                    color=ft.Colors.WHITE,
                ),
                ft.RotatedBox(
                    content=ft.Text(
                        "Filters", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500
                    ),
                    quarter_turns=1,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        width=28,
        height=90,
        bgcolor=FLET_PINK,
        border_radius=ft.BorderRadius(top_left=8, bottom_left=8, top_right=0, bottom_right=0),
        alignment=ft.Alignment.CENTER,
        on_click=lambda _: set_filters_open(not filters_open),
        ink=True,
    )

    toggle_wrapper = ft.Container(
        content=ft.Column(
            controls=[toggle_tab],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        right=260 if filters_open else 0,
        top=0,
        bottom=0,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Results header ---
    results_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "RESULTS",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Container(
                            content=ft.Text(str(state.total_count), size=12, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.PRIMARY,
                            border_radius=4,
                            padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                        ),
                        ft.Text("packages", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                    spacing=8,
                ),
                ft.Row(
                    controls=[
                        ft.Text("SORT BY", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Dropdown(
                            value=state.sort_by,
                            options=sort_items,
                            on_select=lambda e: None,
                            width=180,
                            height=36,
                            text_size=12,
                            border_color=ft.Colors.PRIMARY,
                            color=ft.Colors.PRIMARY,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding(left=20, top=20, right=20, bottom=10),
    )

    return ft.Column(
        controls=[
            # Results header (fixed)
            results_header,
            # Scrollable package list
            ft.Container(
                content=ft.Stack(
                    controls=[
                        ft.ListView(
                            controls=package_list,
                            padding=ft.Padding(left=20, top=0, right=20, bottom=0),
                        ),
                        # Slide-in filter panel
                        filter_panel,
                        # Toggle tab
                        toggle_wrapper,
                    ],
                ),
                expand=True,
            ),
            # Pagination (fixed)
            Pagination(
                current_page=state.page_number,
                total_items=state.total_count,
                per_page=settings.PACKAGES_PER_PAGE,
                on_page_change=lambda p: None,
            ),
            # Footer (fixed at bottom)
            AppFooter(),
        ],
        spacing=0,
        expand=True,
    )
