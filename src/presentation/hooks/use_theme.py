"""Hook for theme management — bridges ThemeState with page-level operations."""

import flet as ft

from src.presentation.state_management.global_state import ThemeState
from src.presentation.themes.colors import DARK_BG, LIGHT_BG


def toggle_theme_mode(page: ft.Page, theme_state: ThemeState) -> None:
    """Toggle between dark and light theme modes."""
    theme_state.is_dark = not theme_state.is_dark
    if theme_state.is_dark:
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = DARK_BG
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = LIGHT_BG
    page.update()
