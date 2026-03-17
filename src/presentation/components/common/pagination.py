import flet as ft

from src.presentation.themes.colors import DARK_ACCENT


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

    def go_to_page(page: int) -> None:
        if on_page_change and 1 <= page <= total_pages:
            on_page_change(page)

    # Build page buttons
    buttons: list[ft.Control] = []

    # Previous
    buttons.append(
        ft.TextButton(
            "<<",
            on_click=lambda _: go_to_page(current_page - 1),
            disabled=current_page <= 1,
            style=ft.ButtonStyle(color=DARK_ACCENT),
        )
    )

    # Page numbers (show max 5 around current)
    start = max(1, current_page - 2)
    end = min(total_pages, start + 4)
    if end - start < 4:
        start = max(1, end - 4)

    for p in range(start, end + 1):
        is_current = p == current_page
        buttons.append(
            ft.TextButton(
                str(p),
                on_click=lambda _, page=p: go_to_page(page),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE if is_current else DARK_ACCENT,
                    bgcolor=DARK_ACCENT if is_current else "transparent",
                ),
            )
        )

    # Next
    buttons.append(
        ft.TextButton(
            ">>",
            on_click=lambda _: go_to_page(current_page + 1),
            disabled=current_page >= total_pages,
            style=ft.ButtonStyle(color=DARK_ACCENT),
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
