"""Package cards — uses ft.Colors.* for theme-aware colors."""

import flet as ft

from src.domain.entities.package import Package
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
            content=ft.Text(f"#{t}", size=12, color=ft.Colors.PRIMARY),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=12,
            padding=ft.Padding(left=8, top=2, right=8, bottom=2),
        )
        for t in package.topics[:5]
    ]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        package.name,
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.PRIMARY,
                                    ),
                                    on_click=handle_click,
                                    ink=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    icon_size=14,
                                    icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                    tooltip=package.pip_install_command,
                                    on_click=handle_copy,
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                _stat_badge(
                                    format_number(package.stars), "LIKES", ft.Colors.PRIMARY
                                ),
                                _stat_badge(
                                    format_number(package.downloads), "DOWNLOADS", ft.Colors.PRIMARY
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    truncate(package.description, 200),
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Row(controls=tags, wrap=True, spacing=6) if tags else ft.Container(),
                ft.Row(
                    controls=[
                        ft.Text(
                            f"v {package.version}" if package.version else "",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            f"({format_date(package.updated_at)})" if package.updated_at else "",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.VERIFIED_USER,
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Text(
                                    package.publisher, size=12, color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                            ],
                            spacing=4,
                        )
                        if package.publisher
                        else ft.Container(),
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.BALANCE, size=12, color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                                ft.Text(
                                    package.license, size=12, color=ft.Colors.ON_SURFACE_VARIANT
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
        border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        on_click=handle_click,
        ink=True,
    )


def _stat_badge(value: str, label: str, color: str) -> ft.Control:
    return ft.Column(
        controls=[
            ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=color),
            ft.Text(label, size=10, color=ft.Colors.ON_SURFACE_VARIANT),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )


@ft.component
def PackageCardSmall(package: Package, on_click: object) -> ft.Control:
    def handle_click(_e: ft.ControlEvent) -> None:
        if on_click:
            on_click(package)

    publisher_row = (
        ft.Row(
            controls=[
                ft.Icon(ft.Icons.VERIFIED, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(
                    package.publisher or package.github_owner,
                    size=11,
                    color=ft.Colors.PRIMARY,
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
                    color=ft.Colors.PRIMARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    truncate(package.description, 100),
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
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
                                ft.Icon(ft.Icons.STAR, size=14, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    format_number(package.stars), size=12, color=ft.Colors.PRIMARY
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DOWNLOAD, size=14, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    format_number(package.downloads),
                                    size=12,
                                    color=ft.Colors.PRIMARY,
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
        height=170,
        padding=16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border=ft.Border(
            left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        ),
        on_click=handle_click,
        ink=True,
    )
