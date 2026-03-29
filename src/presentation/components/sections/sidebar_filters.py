import flet as ft

from config import settings

_CATEGORY_LABELS = {
    "gui": "GUI / UI",
    "mobile": "Mobile",
    "desktop": "Desktop",
    "web": "Web",
    "devtools": "DevTools",
    "database": "Database",
    "media": "Media",
}


@ft.component
def SidebarFilters(
    filter_ui: bool,
    filter_services: bool,
    filter_official: bool,
    filter_categories: list[str],
    on_filter_ui: object,
    on_filter_services: object,
    on_filter_official: object,
    on_toggle_category: object,
) -> ft.Control:
    # Build category checkboxes from settings
    available_categories = list(settings.get("CATEGORIES", {}).keys())
    category_controls: list[ft.Control] = []
    for cat_key in available_categories:
        label = _CATEGORY_LABELS.get(cat_key, cat_key.title())
        is_checked = cat_key in filter_categories
        category_controls.append(
            ft.Checkbox(
                label=label,
                value=is_checked,
                on_change=lambda _, k=cat_key: (
                    on_toggle_category(k) if on_toggle_category else None
                ),
                check_color=ft.Colors.ON_PRIMARY,
                active_color=ft.Colors.PRIMARY,
            )
        )

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
                            "Categories",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                *category_controls,
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
