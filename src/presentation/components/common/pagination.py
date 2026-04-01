"""Pagination — square buttons + per-page selector."""

import flet as ft

from config import settings
from src.presentation.themes.colors import FLET_PINK

PAGE_SIZE_OPTIONS = settings.get("PAGE_SIZE_OPTIONS", [10, 25, 50, 100])


def _page_button(
    label: str,
    is_current: bool,
    on_click: object,
    disabled: bool = False,
) -> ft.Control:
    """Square pagination button."""
    if is_current:
        bg = FLET_PINK
        text_color = ft.Colors.WHITE
    else:
        bg = ft.Colors.SURFACE_CONTAINER_HIGH
        text_color = ft.Colors.ON_SURFACE

    return ft.Container(
        content=ft.Text(
            label,
            size=14,
            color=text_color if not disabled else ft.Colors.ON_SURFACE_VARIANT,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500,
        ),
        width=36,
        height=36,
        border_radius=4,
        bgcolor=bg if not disabled else ft.Colors.SURFACE_CONTAINER,
        alignment=ft.Alignment.CENTER,
        on_click=on_click if not disabled else None,
        ink=not disabled,
    )


@ft.component
def Pagination(
    current_page: int,
    total_items: int,
    per_page: int,
    on_page_change: object,
    on_per_page_change: object = None,
) -> ft.Control:
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    if total_items == 0:
        return ft.Container()

    def go_to_page(page_num: int) -> None:
        if on_page_change and 1 <= page_num <= total_pages:
            on_page_change(page_num)

    # Page buttons — always show, even for a single page
    buttons: list[ft.Control] = []

    buttons.append(
        _page_button(
            "«",
            is_current=False,
            on_click=lambda _: go_to_page(current_page - 1),
            disabled=current_page <= 1,
        )
    )

    start = max(1, current_page - 2)
    end = min(total_pages, start + 4)
    if end - start < 4:
        start = max(1, end - 4)

    for p in range(start, end + 1):
        buttons.append(
            _page_button(
                str(p),
                is_current=(p == current_page),
                on_click=lambda _, pg=p: go_to_page(pg),
            )
        )

    buttons.append(
        _page_button(
            "»",
            is_current=False,
            on_click=lambda _: go_to_page(current_page + 1),
            disabled=current_page >= total_pages,
        )
    )

    # Per-page selector
    per_page_options = [ft.DropdownOption(text=str(n), key=str(n)) for n in PAGE_SIZE_OPTIONS]

    per_page_selector = ft.Row(
        controls=[
            ft.Dropdown(
                value=str(per_page),
                options=per_page_options,
                on_select=lambda e: on_per_page_change(int(e.data)) if on_per_page_change else None,
                width=90,
                text_size=13,
                dense=True,
                content_padding=ft.Padding(left=10, top=0, right=4, bottom=0),
                border_color=ft.Colors.OUTLINE_VARIANT,
                color=ft.Colors.ON_SURFACE,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_radius=4,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                *per_page_selector.controls,
                ft.Container(width=12),
                *buttons,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            wrap=True,
            run_spacing=8,
        ),
        padding=ft.Padding(left=20, top=12, right=20, bottom=12),
    )
