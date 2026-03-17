import flet as ft

from src.presentation.themes.colors import DARK_ACCENT, DARK_CARD, DARK_DIVIDER


@ft.component
def SidebarFilters(
    filter_ui: bool,
    filter_services: bool,
    filter_official: bool,
    filter_screenshot: bool,
    on_filter_ui: object,
    on_filter_services: object,
    on_filter_official: object,
    on_filter_screenshot: object,
) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                # Type section
                ft.Row(
                    controls=[
                        ft.Text(
                            "Type",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Icon(ft.Icons.EXPAND_LESS, color="#9e9e9e", size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                ft.Checkbox(
                    label="UI Controls",
                    value=filter_ui,
                    on_change=lambda e: on_filter_ui(e.data == "true") if on_filter_ui else None,
                    check_color=ft.Colors.WHITE,
                    active_color=DARK_ACCENT,
                ),
                ft.Checkbox(
                    label="Services",
                    value=filter_services,
                    on_change=lambda e: (
                        on_filter_services(e.data == "true") if on_filter_services else None
                    ),
                    check_color=ft.Colors.WHITE,
                    active_color=DARK_ACCENT,
                ),
                ft.Container(height=16),
                ft.Divider(color=DARK_DIVIDER),
                ft.Container(height=8),
                # Advanced section
                ft.Row(
                    controls=[
                        ft.Text(
                            "Advanced",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Icon(ft.Icons.EXPAND_LESS, color="#9e9e9e", size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                ft.Checkbox(
                    label="Developed by Flet Team",
                    value=filter_official,
                    on_change=lambda e: (
                        on_filter_official(e.data == "true") if on_filter_official else None
                    ),
                    check_color=ft.Colors.WHITE,
                    active_color=DARK_ACCENT,
                ),
                ft.Checkbox(
                    label="Has screenshot",
                    value=filter_screenshot,
                    on_change=lambda e: (
                        on_filter_screenshot(e.data == "true") if on_filter_screenshot else None
                    ),
                    check_color=ft.Colors.WHITE,
                    active_color=DARK_ACCENT,
                ),
            ],
        ),
        width=220,
        padding=20,
        bgcolor=DARK_CARD,
        border_radius=8,
    )
