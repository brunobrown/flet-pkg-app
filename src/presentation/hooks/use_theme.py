"""Hook for theme management."""

import flet as ft

from src.presentation.state_management.global_state import AppState


def toggle_theme_mode(page: ft.Page, app_state: AppState) -> None:
    """Toggle between dark and light theme modes."""
    app_state.is_dark = not app_state.is_dark
    if app_state.is_dark:
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    page.update()
