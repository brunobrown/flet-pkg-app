"""Package cards — uses ft.Colors.* for theme-aware colors."""

import flet as ft

from src.domain.entities.package import Package
from src.presentation.themes.colors import FLET_PINK
from src.utils.formatters import format_date, format_number, truncate

_CARD_SHADOW = ft.BoxShadow(
    spread_radius=0,
    blur_radius=8,
    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
    offset=ft.Offset(0, 2),
)

_NEON_BORDER = ft.Border(
    left=ft.BorderSide(1.5, FLET_PINK),
    top=ft.BorderSide(1.5, FLET_PINK),
    right=ft.BorderSide(1.5, FLET_PINK),
    bottom=ft.BorderSide(1.5, FLET_PINK),
)

_DEFAULT_BORDER = ft.Border(
    left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
    top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
    right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
    bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
)


@ft.component
def PackageCard(package: Package, on_click: object, on_copy: object) -> ft.Control:
    hovered, set_hovered = ft.use_state(False)

    def handle_copy(_e: ft.ControlEvent) -> None:
        if on_copy:
            on_copy(package.pip_install_command)

    def handle_click(_e) -> None:
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

    card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    package.name,
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PRIMARY,
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
                                    format_number(package.downloads),
                                    "DOWNLOADS",
                                    ft.Colors.PRIMARY,
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True,
                    run_spacing=4,
                ),
                ft.Text(
                    truncate(package.description, 200),
                    size=14,
                    color=ft.Colors.ON_SURFACE,
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
                                    package.publisher,
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
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
                    wrap=True,
                    run_spacing=4,
                ),
            ],
            spacing=8,
        ),
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        shadow=_CARD_SHADOW,
        border=_NEON_BORDER if hovered else _DEFAULT_BORDER,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    return ft.GestureDetector(
        content=card,
        on_enter=lambda _: set_hovered(True),
        on_exit=lambda _: set_hovered(False),
        on_tap=handle_click,
        mouse_cursor=ft.MouseCursor.CLICK,
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
    hovered, set_hovered = ft.use_state(False)

    def handle_click(_e) -> None:
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

    card = ft.Container(
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
                    color=ft.Colors.ON_SURFACE,
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
                                    format_number(package.stars),
                                    size=12,
                                    color=ft.Colors.PRIMARY,
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
        shadow=_CARD_SHADOW,
        border=_NEON_BORDER if hovered else _DEFAULT_BORDER,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    return ft.GestureDetector(
        content=card,
        on_enter=lambda _: set_hovered(True),
        on_exit=lambda _: set_hovered(False),
        on_tap=handle_click,
        mouse_cursor=ft.MouseCursor.CLICK,
    )


@ft.component
def PackageCardGrid(package: Package, on_click: object, on_copy: object) -> ft.Control:
    """Intermediate card for grid layout — more info than Small, more compact than full."""
    hovered, set_hovered = ft.use_state(False)

    def handle_copy(_e) -> None:
        if on_copy:
            on_copy(package.pip_install_command)

    def handle_click(_e) -> None:
        if on_click:
            on_click(package)

    card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            package.name,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.COPY,
                            icon_size=12,
                            icon_color=ft.Colors.ON_SURFACE_VARIANT,
                            tooltip=package.pip_install_command,
                            on_click=handle_copy,
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(
                    truncate(package.description, 120),
                    size=12,
                    color=ft.Colors.ON_SURFACE,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(expand=True),
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.STAR, size=13, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    format_number(package.stars),
                                    size=12,
                                    color=ft.Colors.PRIMARY,
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DOWNLOAD, size=13, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    format_number(package.downloads),
                                    size=12,
                                    color=ft.Colors.PRIMARY,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            f"v{package.version}" if package.version else "",
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            format_date(package.updated_at) if package.updated_at else "",
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            package.publisher or package.github_owner or "",
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=8,
                    wrap=True,
                    run_spacing=2,
                ),
            ],
            spacing=6,
        ),
        height=180,
        padding=16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        shadow=_CARD_SHADOW,
        border=_NEON_BORDER if hovered else _DEFAULT_BORDER,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    return ft.GestureDetector(
        content=card,
        on_enter=lambda _: set_hovered(True),
        on_exit=lambda _: set_hovered(False),
        on_tap=handle_click,
        mouse_cursor=ft.MouseCursor.CLICK,
    )
