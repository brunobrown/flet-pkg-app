import flet as ft

from src.domain.entities.package import Package
from src.presentation.components.common.package_card import PackageCardSmall
from src.presentation.themes.colors import DARK_ACCENT, DARK_DIVIDER


@ft.component
def PackageSection(
    title: str,
    packages: list[Package],
    on_package_click: object,
    on_view_all: object = None,
    description: str = "",
    max_cards: int = 6,
    cols_per_row: int = 3,
) -> ft.Control:
    if not packages:
        return ft.Container()

    visible = packages[:max_cards]

    # Each card gets a responsive col value:
    # Desktop (LG): cols_per_row cards per row → col = 12 / cols_per_row
    # Tablet (MD): 2 per row → col = 6
    # Mobile (XS): 1 per row → col = 12
    col_lg = 12 // cols_per_row

    cards = []
    for pkg in visible:
        cards.append(
            ft.Container(
                content=PackageCardSmall(pkg, on_package_click),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 12,
                    ft.ResponsiveRowBreakpoint.SM: 6,
                    ft.ResponsiveRowBreakpoint.MD: 6,
                    ft.ResponsiveRowBreakpoint.LG: col_lg,
                },
            )
        )

    controls: list[ft.Control] = [
        ft.Text(
            title,
            size=22,
            weight=ft.FontWeight.W_500,
            color=DARK_ACCENT,
        ),
    ]

    if description:
        controls.append(
            ft.Text(description, size=14, color="#9e9e9e"),
        )

    controls.append(ft.Container(height=16))

    controls.append(
        ft.ResponsiveRow(
            controls=cards,
            spacing=12,
            run_spacing=12,
        )
    )

    if on_view_all:
        controls.append(
            ft.Container(
                content=ft.TextButton(
                    "VIEW ALL",
                    on_click=lambda _: on_view_all(),
                    style=ft.ButtonStyle(color=DARK_ACCENT),
                ),
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.Padding(left=0, top=4, right=0, bottom=0),
            )
        )

    return ft.Container(
        content=ft.Column(controls=controls, spacing=4),
        padding=ft.Padding(left=40, top=30, right=40, bottom=20),
        border=ft.Border(bottom=ft.BorderSide(1, DARK_DIVIDER)),
    )
