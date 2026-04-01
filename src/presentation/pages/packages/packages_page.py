"""Packages list page — slide-in filter panel like detail page sidebar."""

import flet as ft

from config import settings
from src.presentation.components.common.footer import AppFooter
from src.presentation.components.common.loading import ErrorMessage
from src.presentation.components.common.package_card import PackageCardGrid
from src.presentation.components.common.pagination import Pagination
from src.presentation.components.common.skeleton_card import SkeletonCardList
from src.presentation.components.sections.sidebar_filters import SidebarFilters
from src.presentation.state_management.app_context import AppCtx
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
    ctx = ft.use_context(AppCtx)
    filters_open, set_filters_open = ft.use_state(False)

    # Derive filter checkbox values from observable state (not use_state)
    # so they survive re-renders triggered by @ft.observable changes.
    filter_ui = state.filter_type == "UI Controls"
    filter_services = state.filter_type == "Services"
    filter_official = state.filter_official
    filter_categories = state.filter_categories

    # --- Handlers that update state and re-search ---
    def handle_page_change(page_num: int) -> None:
        state.page_number = page_num
        ctx.reload_packages()

    def handle_per_page_change(value: int) -> None:
        state.per_page = value
        state.page_number = 1
        ft.context.page.run_task(ft.SharedPreferences().set, "per_page", value)
        ctx.reload_packages()

    def handle_sort_change(sort_value: str) -> None:
        state.sort_by = sort_value
        state.page_number = 1
        ctx.reload_packages()

    def handle_filter_ui(value: bool) -> None:
        if value:
            state.filter_type = "UI Controls"
        elif state.filter_type == "UI Controls":
            state.filter_type = None
        state.page_number = 1
        ctx.reload_packages()

    def handle_filter_services(value: bool) -> None:
        if value:
            state.filter_type = "Services"
        elif state.filter_type == "Services":
            state.filter_type = None
        state.page_number = 1
        ctx.reload_packages()

    def handle_filter_official(value: bool) -> None:
        state.filter_official = value
        state.page_number = 1
        ctx.reload_packages()

    def handle_toggle_category(cat_key: str) -> None:
        cats = list(state.filter_categories)
        if cat_key in cats:
            cats.remove(cat_key)
        else:
            cats.append(cat_key)
        state.filter_categories = cats
        state.page_number = 1
        ctx.reload_packages()

    # Build package list from state
    package_list: list[ft.Control] = []
    if state.is_loading:
        package_list.append(SkeletonCardList(count=state.per_page))
    elif state.error:
        package_list.append(ErrorMessage(state.error))
    elif not state.packages:
        package_list.append(
            ft.Container(
                content=ft.Text(
                    "No flet packages were found", color=ft.Colors.ON_SURFACE_VARIANT, size=16
                ),
                padding=40,
                alignment=ft.Alignment.CENTER,
            )
        )
    else:
        grid_cards = []
        for pkg in state.packages:
            grid_cards.append(
                ft.Container(
                    content=PackageCardGrid(
                        pkg,
                        on_click=on_package_click,
                        on_copy=on_copy,
                        on_search=ctx.search,
                    ),
                    col={
                        ft.ResponsiveRowBreakpoint.XS: 12,
                        ft.ResponsiveRowBreakpoint.SM: 6,
                        ft.ResponsiveRowBreakpoint.LG: 4,
                    },
                )
            )
        package_list.append(ft.ResponsiveRow(controls=grid_cards, spacing=10, run_spacing=10))

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
                filter_categories=filter_categories,
                on_filter_ui=handle_filter_ui,
                on_filter_services=handle_filter_services,
                on_filter_official=handle_filter_official,
                on_toggle_category=handle_toggle_category,
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
        content=toggle_tab,
        right=260 if filters_open else 0,
        top=200,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Results header ---
    def _results_info() -> ft.Row:
        return ft.Row(
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
        )

    # Desktop results header: results info + sort dropdown
    results_header_desktop = ft.Container(
        content=ft.Row(
            controls=[
                _results_info(),
                ft.Row(
                    controls=[
                        # ft.Text("SORT BY", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Dropdown(
                            value=state.sort_by,
                            options=sort_items,
                            on_select=lambda e: handle_sort_change(e.data),
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
        padding=ft.Padding(left=20, top=20, right=20, bottom=20),
        col={ft.ResponsiveRowBreakpoint.XS: 0, ft.ResponsiveRowBreakpoint.MD: 12},
    )

    # Mobile results header: results info + sort popup icon
    results_header_mobile = ft.Container(
        content=ft.Row(
            controls=[
                _results_info(),
                ft.PopupMenuButton(
                    content=ft.Container(
                        content=ft.Icon(ft.Icons.SORT, size=22, color=ft.Colors.WHITE),
                        width=40,
                        height=40,
                        border_radius=20,
                        bgcolor=ft.Colors.PRIMARY,
                        alignment=ft.Alignment.CENTER,
                    ),
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Text(s, size=13),
                            on_click=lambda _, _s=s: handle_sort_change(_s),
                        )
                        for s in settings.SORT_OPTIONS
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=20, top=16, right=20, bottom=8),
        col={ft.ResponsiveRowBreakpoint.XS: 12, ft.ResponsiveRowBreakpoint.MD: 0},
    )

    results_header = ft.ResponsiveRow(
        controls=[results_header_desktop, results_header_mobile],
        spacing=0,
        run_spacing=0,
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
                            scroll=ft.Scrollbar(
                                thumb_visibility=True,
                                interactive=True,
                            ),
                            controls=[
                                *package_list,
                                # Pagination + footer scroll with content
                                Pagination(
                                    current_page=state.page_number,
                                    total_items=state.total_count,
                                    per_page=state.per_page,
                                    on_page_change=handle_page_change,
                                    on_per_page_change=handle_per_page_change,
                                ),
                                AppFooter(),
                            ],
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
        ],
        spacing=0,
        expand=True,
    )
