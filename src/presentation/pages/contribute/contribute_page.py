"""Contribute page — support the project + social links."""

import flet as ft

from src.presentation.components.common.footer import AppFooter
from src.presentation.themes.colors import FLET_PINK


@ft.component
def ContributePage() -> ft.Control:
    def _open_url(url: str) -> None:
        ft.context.page.run_task(ft.UrlLauncher().launch_url, url)

    def _social_button(icon_src: str, label: str, url: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src=icon_src, width=20, height=20, fit=ft.BoxFit.CONTAIN),
                    ft.Text(label, size=14, color=ft.Colors.ON_SURFACE, weight=ft.FontWeight.W_500),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, top=10, right=20, bottom=10),
            border_radius=8,
            border=ft.Border(
                left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            ),
            on_click=lambda _: _open_url(url),
            ink=True,
        )

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.FAVORITE, size=28, color=FLET_PINK),
                                ft.Text(
                                    "Support & Contribute",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Help us build the best package discovery "
                            "platform for the Flet ecosystem",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding(left=40, top=20, right=40, bottom=12),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            ),
            ft.Container(
                content=ft.ListView(
                    scroll=ft.Scrollbar(thumb_visibility=True, interactive=True),
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    # --- Buy Me a Coffee ---
                                    ft.Container(height=20),
                                    ft.Text(
                                        "Buy Me a Coffee",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                    ft.Container(height=8),
                                    ft.Text(
                                        "If you find Flet PKG useful, please consider "
                                        "supporting its development. Every coffee helps "
                                        "keep the project alive and growing!",
                                        size=14,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                    ft.Container(height=16),
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Image(
                                                    src="/icons/bmc-button.png",
                                                    width=300,
                                                    height=70,
                                                    fit=ft.BoxFit.COVER,
                                                ),
                                            ],
                                            spacing=10,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        bgcolor="#FFDD00",
                                        padding=ft.Padding(left=24, top=12, right=24, bottom=12),
                                        border_radius=12,
                                        on_click=lambda _: _open_url(
                                            "https://www.buymeacoffee.com/brunobrown"
                                        ),
                                        ink=True,
                                        width=500,
                                    ),
                                    # --- Social Links ---
                                    ft.Container(height=40),
                                    ft.Text(
                                        "Connect with Me",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                    ft.Container(height=8),
                                    ft.Text(
                                        "Follow the project and get in touch through social media.",
                                        size=14,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                    ft.Container(height=16),
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=_social_button(
                                                    "/icons/github.png",
                                                    "GitHub",
                                                    "https://github.com/brunobrown",
                                                ),
                                                width=150,
                                            ),
                                            ft.Container(
                                                content=_social_button(
                                                    "/icons/linkedin.png",
                                                    "LinkedIn",
                                                    "https://linkedin.com/in/bruno-brown-29418167",
                                                ),
                                                width=150,
                                            ),
                                            ft.Container(
                                                content=_social_button(
                                                    "/icons/twitter.png",
                                                    "X (Twitter)",
                                                    "https://x.com/BrunoBrown86",
                                                ),
                                                width=150,
                                            ),
                                        ],
                                        spacing=10,
                                        run_spacing=10,
                                    ),
                                    # --- Contributing ---
                                    ft.Container(height=40),
                                    ft.Text(
                                        "Contributing",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                    ft.Container(height=8),
                                    ft.Text(
                                        "Flet PKG is open source! Contributions are welcome — "
                                        "whether it's bug reports, feature requests, "
                                        "or pull requests.",
                                        size=14,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                    ft.Container(height=12),
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.CODE,
                                                    size=18,
                                                    color=ft.Colors.PRIMARY,
                                                ),
                                                ft.Text(
                                                    "View on GitHub",
                                                    size=14,
                                                    color=ft.Colors.PRIMARY,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                            ],
                                            spacing=8,
                                        ),
                                        on_click=lambda _: _open_url(
                                            "https://github.com/brunobrown/flet-pkg-app"
                                        ),
                                        ink=True,
                                        padding=ft.Padding(left=0, top=4, right=0, bottom=4),
                                    ),
                                    ft.Container(height=20),
                                ],
                                spacing=0,
                            ),
                            padding=ft.Padding(left=40, top=0, right=40, bottom=20),
                        ),
                    ],
                ),
                expand=True,
            ),
            AppFooter(),
        ],
        spacing=0,
        expand=True,
    )
