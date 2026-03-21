"""Responsive header component.

Desktop (MD+): center logo+title, right Help+theme. No hamburger.
Mobile (XS): left hamburger, center logo+title, right theme. No Help.
"""

import flet as ft

from src.presentation.themes.colors import FLET_BLUE_LIGHT


@ft.component
def AppHeader(
    on_theme_toggle: object = None,
    on_open_drawer: object = None,
    on_navigate_home: object = None,
) -> ft.Control:
    # --- Desktop header (hidden on mobile) ---
    desktop_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Image(
                                src="/images/flet.svg",
                                width=28,
                                height=28,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                            ft.Text(
                                "Flet PKG",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=8,
                    ),
                    on_click=lambda _: on_navigate_home() if on_navigate_home else None,
                    ink=True,
                ),
                ft.Container(expand=True),
                ft.PopupMenuButton(
                    content=ft.Row(
                        controls=[
                            ft.Text("Help", color=ft.Colors.WHITE, size=13),
                            ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.WHITE, size=16),
                        ],
                        spacing=0,
                    ),
                    items=[
                        ft.PopupMenuItem(content="About Flet PKG"),
                        ft.PopupMenuItem(content="Flet Documentation"),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_6,
                    icon_color=FLET_BLUE_LIGHT,
                    icon_size=20,
                    on_click=lambda _: on_theme_toggle() if on_theme_toggle else None,
                    tooltip="Toggle theme",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        col={
            ft.ResponsiveRowBreakpoint.XS: 0,
            ft.ResponsiveRowBreakpoint.MD: 12,
        },
    )

    # --- Mobile header (hidden on desktop) ---
    mobile_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE,
                    icon_size=24,
                    on_click=lambda _: on_open_drawer() if on_open_drawer else None,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Image(
                                src="/images/flet.svg",
                                width=28,
                                height=28,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                            ft.Text(
                                "Flet PKG",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=8,
                    ),
                    on_click=lambda _: on_navigate_home() if on_navigate_home else None,
                    ink=True,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_6,
                    icon_color=FLET_BLUE_LIGHT,
                    icon_size=20,
                    on_click=lambda _: on_theme_toggle() if on_theme_toggle else None,
                    tooltip="Toggle theme",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        col={
            ft.ResponsiveRowBreakpoint.XS: 12,
            ft.ResponsiveRowBreakpoint.MD: 0,
        },
    )

    return ft.Container(
        content=ft.ResponsiveRow(
            controls=[desktop_header, mobile_header],
            spacing=0,
        ),
        bgcolor="#081425",
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
    )
