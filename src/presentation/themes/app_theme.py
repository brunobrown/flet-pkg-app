"""Theme configuration — Dark and Light themes with full ColorScheme.

All components should use ft.Colors.* semantic colors instead of hardcoded hex.
The ColorScheme maps these to the correct values for each mode.
"""

import flet as ft

from src.presentation.themes.colors import FLET_BLUE, FLET_BLUE_LIGHT


def get_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=FLET_BLUE,
        color_scheme=ft.ColorScheme(
            primary=FLET_BLUE_LIGHT,
            on_primary="#081425",
            secondary=FLET_BLUE,
            on_secondary=ft.Colors.WHITE,
            surface="#14253A",
            on_surface="#EFF0F3",
            on_surface_variant="#8A92A2",
            surface_container_lowest="#081425",
            surface_container_low="#0f1d30",
            surface_container="#14253A",
            surface_container_high="#232831",
            surface_container_highest="#2d3444",
            outline_variant="#354457",
            inverse_surface="#EFF0F3",
            on_inverse_surface="#081425",
        ),
    )


def get_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=FLET_BLUE,
        color_scheme=ft.ColorScheme(
            primary=FLET_BLUE,
            on_primary=ft.Colors.WHITE,
            secondary=FLET_BLUE_LIGHT,
            on_secondary=ft.Colors.WHITE,
            surface="#ffffff",
            on_surface="#212121",
            on_surface_variant="#757575",
            surface_container_lowest="#f5f5f5",
            surface_container_low="#f0f0f0",
            surface_container="#e8e8e8",
            surface_container_high="#e0e0e0",
            surface_container_highest="#d6d6d6",
            outline_variant="#e0e0e0",
            inverse_surface="#212121",
            on_inverse_surface="#ffffff",
        ),
    )
