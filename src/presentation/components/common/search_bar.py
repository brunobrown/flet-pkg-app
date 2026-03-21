"""Hero search bar — search field + subtitle only. Logo/title are in the AppBar."""

import flet as ft

from src.presentation.themes.colors import DARK_ACCENT


@ft.component
def HeroSearchBar(on_search: object) -> ft.Control:
    query, set_query = ft.use_state("")

    def handle_search_submit(e: ft.ControlEvent) -> None:
        text = e.data or query
        if on_search and text:
            on_search(text)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Container(
                    content=ft.TextField(
                        value=query,
                        hint_text="Search packages",
                        on_change=lambda e: set_query(e.data or ""),
                        on_submit=handle_search_submit,
                        border_radius=30,
                        content_padding=ft.Padding(left=20, top=14, right=20, bottom=14),
                        border_color="transparent",
                        focused_border_color="#354457",
                        cursor_color=DARK_ACCENT,
                        text_size=16,
                        prefix_icon=ft.Icons.SEARCH,
                        bgcolor="#232831",
                        hint_style=ft.TextStyle(color="#8A92A2"),
                    ),
                    width=650,
                ),
                ft.Container(height=8),
                ft.Text(
                    "The package discovery platform for Dart and Flet apps.",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color="#8A92A2",
                ),
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=10),
        alignment=ft.Alignment.CENTER,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#081425", "#14253A", "#081425"],
        ),
    )
