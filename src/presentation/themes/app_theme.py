import flet as ft

from src.presentation.themes.colors import FLET_BLUE, FLET_BLUE_LIGHT


def get_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=FLET_BLUE,
        color_scheme=ft.ColorScheme(
            primary=FLET_BLUE_LIGHT,
            on_primary=ft.Colors.WHITE,
            secondary=FLET_BLUE,
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
            label_large=ft.TextStyle(color=FLET_BLUE_LIGHT),
            label_medium=ft.TextStyle(color="#9e9e9e"),
            label_small=ft.TextStyle(color="#757575"),
        ),
    )


def get_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=FLET_BLUE,
        color_scheme=ft.ColorScheme(
            primary=FLET_BLUE,
            on_primary=ft.Colors.WHITE,
            secondary=FLET_BLUE_LIGHT,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
            surface_container_lowest="#f5f5f5",
        ),
    )
