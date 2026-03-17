import flet as ft

from src.presentation.themes.colors import DARK_ACCENT


@ft.component
def HeroSearchBar(
    on_search: object,
    on_theme_toggle: object = None,
) -> ft.Control:
    query, set_query = ft.use_state("")

    def handle_search_submit(e: ft.ControlEvent) -> None:
        """Handle Enter key — use e.data which contains the current text."""
        text = e.data or query
        if on_search and text:
            on_search(text)

    # Top-right toolbar (Help + Theme toggle) like pub.dev
    top_bar = ft.Container(
        content=ft.Row(
            controls=[
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
                    icon_color=ft.Colors.WHITE,
                    icon_size=20,
                    on_click=lambda _: on_theme_toggle() if on_theme_toggle else None,
                    tooltip="Toggle theme",
                ),
            ],
            spacing=0,
        ),
        padding=ft.Padding(left=0, top=0, right=8, bottom=0),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                top_bar,
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.Image(
                            src="/images/flet.svg",
                            width=52,
                            height=52,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        ft.Text(
                            "Flet PKG",
                            size=42,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.TextField(
                        value=query,
                        hint_text="Search packages",
                        on_change=lambda e: set_query(e.data or ""),
                        on_submit=handle_search_submit,
                        border_radius=30,
                        content_padding=ft.Padding(left=20, top=14, right=20, bottom=14),
                        border_color="transparent",
                        focused_border_color="#4a4f6a",
                        cursor_color=DARK_ACCENT,
                        text_size=16,
                        prefix_icon=ft.Icons.SEARCH,
                        bgcolor="#3a3f5a",
                        hint_style=ft.TextStyle(color="#8a8fa0"),
                    ),
                    width=650,
                ),
                ft.Container(height=8),
                ft.Text(
                    "The package discovery platform for Dart and Flet apps.",
                    size=15,
                    text_align=ft.TextAlign.CENTER,
                    color="#9e9eae",
                ),
                ft.Container(height=16),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        alignment=ft.Alignment.CENTER,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#1a1a2e", "#16213e", "#1a1a2e"],
        ),
    )
