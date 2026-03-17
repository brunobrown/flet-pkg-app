import flet as ft


def get_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=ft.Colors.CYAN,
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.CYAN_400,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.CYAN_700,
            surface="#1e2337",
            on_surface=ft.Colors.WHITE,
            surface_container_lowest="#1a1a2e",
            surface_container_low="#1e2337",
        ),
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(color=ft.Colors.WHITE),
            display_medium=ft.TextStyle(color=ft.Colors.WHITE),
            display_small=ft.TextStyle(color=ft.Colors.WHITE),
            headline_large=ft.TextStyle(color=ft.Colors.WHITE),
            headline_medium=ft.TextStyle(color=ft.Colors.WHITE),
            headline_small=ft.TextStyle(color=ft.Colors.WHITE),
            title_large=ft.TextStyle(color=ft.Colors.WHITE),
            title_medium=ft.TextStyle(color=ft.Colors.WHITE),
            title_small=ft.TextStyle(color=ft.Colors.WHITE),
            body_large=ft.TextStyle(color="#e0e0e0"),
            body_medium=ft.TextStyle(color="#e0e0e0"),
            body_small=ft.TextStyle(color="#9e9e9e"),
            label_large=ft.TextStyle(color=ft.Colors.CYAN_400),
            label_medium=ft.TextStyle(color="#9e9e9e"),
            label_small=ft.TextStyle(color="#757575"),
        ),
    )


def get_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_700,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.BLUE_400,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
            surface_container_lowest="#f5f5f5",
        ),
    )
