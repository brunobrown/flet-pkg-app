"""App footer — single line with icon links."""

import flet as ft


@ft.component
def AppFooter() -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "Flet PKG",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Container(width=16),
                            ft.IconButton(
                                icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url="https://discord.gg/dzWXP8SHG8",
                                tooltip="Discord",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CODE,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url="https://github.com/flet-dev/flet",
                                tooltip="GitHub",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARTICLE_OUTLINED,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url="https://flet.dev/blog/",
                                tooltip="Blog",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.SUPPORT,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                icon_size=18,
                                url="https://flet.dev/support/",
                                tooltip="Support",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=ft.Padding(left=0, top=8, right=0, bottom=12),
                ),
            ],
            spacing=0,
        ),
        padding=ft.Padding(left=20, top=10, right=20, bottom=0),
    )
