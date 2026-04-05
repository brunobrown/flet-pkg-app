"""Hero search bar — background image + logo + title like pub.dev."""

import flet as ft


@ft.component
def HeroSearchBar(on_search: object) -> ft.Control:
    query, set_query = ft.use_state("")

    def handle_search_submit(e: ft.ControlEvent) -> None:
        text = e.data if e.data is not None else query
        if on_search:
            on_search(text)

    def handle_clear(_e: ft.ControlEvent) -> None:
        set_query("")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=120),
                # Logo + Title (like pub.dev)
                ft.Row(
                    controls=[
                        ft.Image(
                            src="/images/flet.svg",
                            width=72,
                            height=72,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        ft.Text(
                            "Flet PKG",
                            size=52,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Container(height=24),
                # Search field (gray semi-transparent like pub.dev)
                ft.Container(
                    content=ft.TextField(
                        value=query,
                        hint_text="Search packages",
                        on_change=lambda e: set_query(e.data or ""),
                        on_submit=handle_search_submit,
                        border_radius=30,
                        content_padding=ft.Padding(left=24, top=18, right=24, bottom=18),
                        border_color="transparent",
                        focused_border_color="#4a5568",
                        cursor_color=ft.Colors.WHITE,
                        text_size=18,
                        prefix_icon=ft.Icons.SEARCH,
                        suffix=ft.Container(
                            content=ft.Icon(ft.Icons.CLOSE, size=18, color="#9eafc0"),
                            on_click=handle_clear,
                            ink=True,
                            tooltip="Clear search",
                        )
                        if query
                        else None,
                        bgcolor="#3d4557",
                        hint_style=ft.TextStyle(color="#9eafc0"),
                        color=ft.Colors.WHITE,
                    ),
                    width=650,
                ),
                ft.Container(height=12),
                ft.Text(
                    "The package discovery platform for Flet apps.",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color="#9eafc0",
                ),
                ft.Container(height=120),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=10),
        alignment=ft.Alignment.CENTER,
        bgcolor="#14253A",
        image=ft.DecorationImage(
            src="/images/hero-bg-static.png",
            fit=ft.BoxFit.COVER,
            opacity=0.1,
        ),
    )
