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
) -> ft.Control:
    if not packages:
        return ft.Container()

    cards = [PackageCardSmall(pkg, on_package_click) for pkg in packages]

    controls: list[ft.Control] = [
        # Section title (colored, like pub.dev)
        ft.Text(
            title,
            size=22,
            weight=ft.FontWeight.W_500,
            color=DARK_ACCENT,
        ),
    ]

    if description:
        controls.append(
            ft.Text(
                description,
                size=14,
                color="#9e9e9e",
            )
        )

    controls.append(ft.Container(height=16))

    # Cards in a horizontal scrollable row (left-aligned like pub.dev)
    controls.append(
        ft.Row(
            controls=cards,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        )
    )

    # VIEW ALL link (right-aligned, uppercase, like pub.dev)
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
