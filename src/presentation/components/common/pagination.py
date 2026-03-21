"""Pagination — square numbered buttons like pub.dev, active in Flet pink."""

import flet as ft

from src.presentation.themes.colors import FLET_PINK


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
) -> ft.Control:
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    if total_pages <= 1:
        return ft.Container()

    def go_to_page(page_num: int) -> None:
        if on_page_change and 1 <= page_num <= total_pages:
            on_page_change(page_num)

    buttons: list[ft.Control] = []

    # Previous «
    buttons.append(
        _page_button(
            "«",
            is_current=False,
            on_click=lambda _: go_to_page(current_page - 1),
            disabled=current_page <= 1,
        )
    )

    # Page numbers
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

    # Next »
    buttons.append(
        _page_button(
            "»",
            is_current=False,
            on_click=lambda _: go_to_page(current_page + 1),
            disabled=current_page >= total_pages,
        )
    )

    return ft.Container(
        content=ft.Row(
            controls=buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.Padding(left=0, top=20, right=0, bottom=20),
    )
