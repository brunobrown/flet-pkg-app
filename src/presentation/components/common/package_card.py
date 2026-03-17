import flet as ft

from src.domain.entities.package import Package
from src.presentation.themes.colors import (
    DARK_ACCENT,
    DARK_CARD,
    DARK_DIVIDER,
    TAG_BG,
    TAG_COLOR,
)
from src.utils.formatters import format_date, format_number, truncate


@ft.component
def PackageCard(package: Package, on_click: object, on_copy: object) -> ft.Control:
    def handle_copy(_e: ft.ControlEvent) -> None:
        if on_copy:
            on_copy(package.pip_install_command)

    def handle_click(_e: ft.ControlEvent) -> None:
        if on_click:
            on_click(package)

    tags = [
        ft.Container(
            content=ft.Text(f"#{t}", size=12, color=TAG_COLOR),
            bgcolor=TAG_BG,
            border_radius=12,
            padding=ft.Padding(left=8, top=2, right=8, bottom=2),
        )
        for t in package.topics[:5]
    ]

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header row: name + copy + stats
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        package.name,
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=DARK_ACCENT,
                                    ),
                                    on_click=handle_click,
                                    ink=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    icon_size=14,
                                    icon_color="#9e9e9e",
                                    tooltip=package.pip_install_command,
                                    on_click=handle_copy,
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                _stat_badge(
                                    format_number(package.stars),
                                    "LIKES",
                                    DARK_ACCENT,
                                ),
                                _stat_badge(
                                    format_number(package.downloads),
                                    "DOWNLOADS",
                                    DARK_ACCENT,
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Description
                ft.Text(
                    truncate(package.description, 200),
                    size=14,
                    color="#bdbdbd",
                ),
                # Tags
                ft.Row(controls=tags, wrap=True, spacing=6) if tags else ft.Container(),
                # Metadata row
                ft.Row(
                    controls=[
                        ft.Text(
                            f"v {package.version}" if package.version else "",
                            size=12,
                            color="#757575",
                        ),
                        ft.Text(
                            f"({format_date(package.updated_at)})" if package.updated_at else "",
                            size=12,
                            color="#757575",
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.VERIFIED_USER,
                                    size=12,
                                    color="#757575",
                                ),
                                ft.Text(
                                    package.publisher,
                                    size=12,
                                    color="#757575",
                                ),
                            ],
                            spacing=4,
                        )
                        if package.publisher
                        else ft.Container(),
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.BALANCE,
                                    size=12,
                                    color="#757575",
                                ),
                                ft.Text(
                                    package.license,
                                    size=12,
                                    color="#757575",
                                ),
                            ],
                            spacing=4,
                        )
                        if package.license
                        else ft.Container(),
                    ],
                    spacing=12,
                ),
            ],
            spacing=8,
        ),
        padding=20,
        border=ft.Border(bottom=ft.BorderSide(1, DARK_DIVIDER)),
        bgcolor=DARK_CARD,
        on_click=handle_click,
        ink=True,
    )


def _stat_badge(value: str, label: str, color: str) -> ft.Control:
    return ft.Column(
        controls=[
            ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=color),
            ft.Text(label, size=10, color="#757575"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )


@ft.component
def PackageCardSmall(package: Package, on_click: object) -> ft.Control:
    """Card for the home page sections — wider, with publisher link like pub.dev."""

    def handle_click(_e: ft.ControlEvent) -> None:
        if on_click:
            on_click(package)

    # Publisher row
    publisher_row = (
        ft.Row(
            controls=[
                ft.Icon(ft.Icons.VERIFIED, size=12, color="#757575"),
                ft.Text(
                    package.publisher or package.github_owner,
                    size=11,
                    color=DARK_ACCENT,
                ),
            ],
            spacing=4,
        )
        if (package.publisher or package.github_owner)
        else ft.Container()
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    package.name,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_ACCENT,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    truncate(package.description, 100),
                    size=12,
                    color="#bdbdbd",
                    max_lines=3,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(expand=True),
                publisher_row,
                ft.Container(height=4),
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.STAR, size=14, color=DARK_ACCENT),
                                ft.Text(
                                    format_number(package.stars),
                                    size=12,
                                    color=DARK_ACCENT,
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DOWNLOAD, size=14, color=DARK_ACCENT),
                                ft.Text(
                                    format_number(package.downloads),
                                    size=12,
                                    color=DARK_ACCENT,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=4,
        ),
        width=250,
        height=170,
        padding=16,
        border_radius=8,
        bgcolor=DARK_CARD,
        border=ft.Border(
            left=ft.BorderSide(1, DARK_DIVIDER),
            top=ft.BorderSide(1, DARK_DIVIDER),
            right=ft.BorderSide(1, DARK_DIVIDER),
            bottom=ft.BorderSide(1, DARK_DIVIDER),
        ),
        on_click=handle_click,
        ink=True,
    )
