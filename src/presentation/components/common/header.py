import flet as ft

from src.presentation.themes.colors import DARK_ACCENT, DARK_HEADER


@ft.component
def AppHeader(
    on_search: object,
    on_theme_toggle: object,
    on_navigate_home: object,
    search_query: str = "",
) -> ft.Control:
    query, set_query = ft.use_state(search_query)

    def handle_search(e: ft.ControlEvent) -> None:
        if on_search:
            on_search(query)

    return ft.Container(
        content=ft.Row(
            controls=[
                # Logo (arrow icon like pub.dev)
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ARROW_BACK_IOS_NEW,
                        color=DARK_ACCENT,
                        size=28,
                    ),
                    on_click=lambda _: on_navigate_home() if on_navigate_home else None,
                    ink=True,
                    padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                ),
                # Search bar (centered, like pub.dev)
                ft.Container(
                    content=ft.TextField(
                        value=query,
                        hint_text="Search packages",
                        on_change=lambda e: set_query(e.control.value),
                        on_submit=lambda e: handle_search(e),
                        border_radius=25,
                        content_padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                        border_color="transparent",
                        focused_border_color="#4a4f6a",
                        cursor_color=DARK_ACCENT,
                        text_size=14,
                        prefix_icon=ft.Icons.SEARCH,
                        height=42,
                        bgcolor="#2d3250",
                        hint_style=ft.TextStyle(color="#8a8fa0"),
                    ),
                    expand=True,
                    padding=ft.Padding(left=20, top=0, right=20, bottom=0),
                ),
                # Right side: Help + Theme toggle
                ft.Row(
                    controls=[
                        ft.PopupMenuButton(
                            content=ft.Text("Help", color=ft.Colors.WHITE, size=14),
                            items=[
                                ft.PopupMenuItem(content="About Flet PKG"),
                                ft.PopupMenuItem(content="Flet Documentation"),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.BRIGHTNESS_6,
                            icon_color=ft.Colors.WHITE,
                            icon_size=20,
                            on_click=lambda _: on_theme_toggle() if on_theme_toggle else None,
                            tooltip="Toggle theme",
                        ),
                    ],
                    spacing=0,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=DARK_HEADER,
        padding=ft.Padding(left=16, top=8, right=16, bottom=8),
    )
