import flet as ft


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
                ft.Row(
                    controls=[
                        ft.Text(
                            "Type", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE
                        ),
                        ft.Icon(ft.Icons.EXPAND_LESS, color=ft.Colors.ON_SURFACE_VARIANT, size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                ft.Checkbox(
                    label="UI Controls",
                    value=filter_ui,
                    on_change=lambda e: on_filter_ui(e.data == "true") if on_filter_ui else None,
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
                ft.Checkbox(
                    label="Services",
                    value=filter_services,
                    on_change=lambda e: (
                        on_filter_services(e.data == "true") if on_filter_services else None
                    ),
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
                ft.Container(height=16),
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Advanced",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Icon(ft.Icons.EXPAND_LESS, color=ft.Colors.ON_SURFACE_VARIANT, size=20),
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
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
                ft.Checkbox(
                    label="Has screenshot",
                    value=filter_screenshot,
                    on_change=lambda e: (
                        on_filter_screenshot(e.data == "true") if on_filter_screenshot else None
                    ),
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
            ],
        ),
        width=220,
        padding=20,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        border_radius=8,
    )
