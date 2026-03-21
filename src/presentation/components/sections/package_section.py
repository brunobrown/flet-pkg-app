import flet as ft

from src.domain.entities.package import Package
from src.presentation.components.common.package_card import PackageCardSmall
from src.presentation.themes.colors import DARK_ACCENT


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

    col_lg = 12 // cols_per_row

    cards = []
    for pkg in visible:
        cards.append(
            ft.Container(
                content=PackageCardSmall(pkg, on_package_click),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 6,
                    ft.ResponsiveRowBreakpoint.SM: 6,
                    ft.ResponsiveRowBreakpoint.MD: 6,
                    ft.ResponsiveRowBreakpoint.LG: col_lg,
                },
            )
        )

    # Section header
    header_controls: list[ft.Control] = [
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color="#EFF0F3",
        ),
    ]

    if description:
        header_controls.append(
            ft.Text(description, size=13, color="#8A92A2"),
        )

    # VIEW ALL link
    footer: list[ft.Control] = []
    if on_view_all:
        footer.append(
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

    # Section container with background (like in the design)
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Column(controls=header_controls, spacing=2),
                ft.Container(height=12),
                # Cards grid
                ft.ResponsiveRow(controls=cards, spacing=10, run_spacing=10),
                # Footer
                *footer,
            ],
            spacing=0,
        ),
        bgcolor="#14253A",
        border_radius=12,
        padding=ft.Padding(left=20, top=20, right=20, bottom=16),
        margin=ft.Margin(left=20, top=16, right=20, bottom=0),
    )
