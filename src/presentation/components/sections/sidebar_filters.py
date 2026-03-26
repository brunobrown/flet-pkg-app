import flet as ft


@ft.component
def SidebarFilters(
    filter_ui: bool,
    filter_services: bool,
    filter_official: bool,
    on_filter_ui: object,
    on_filter_services: object,
    on_filter_official: object,
) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Type", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                ft.Checkbox(
                    label="UI Controls",
                    value=filter_ui,
                    on_change=lambda _: on_filter_ui(not filter_ui) if on_filter_ui else None,
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
                ft.Checkbox(
                    label="Services",
                    value=filter_services,
                    on_change=lambda _: (
                        on_filter_services(not filter_services) if on_filter_services else None
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
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                ft.Checkbox(
                    label="Developed by Flet Team",
                    value=filter_official,
                    on_change=lambda _: (
                        on_filter_official(not filter_official) if on_filter_official else None
                    ),
                    check_color=ft.Colors.ON_PRIMARY,
                    active_color=ft.Colors.PRIMARY,
                ),
            ],
        ),
    )
