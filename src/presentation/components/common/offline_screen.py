"""Offline screen — shown when device has no internet connectivity."""

import flet as ft


@ft.component
def OfflineScreen() -> ft.Control:
    """Full-screen offline indicator.

    Connectivity is monitored automatically — the screen disappears
    when internet is restored (via Connectivity.on_change).
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.WIFI_OFF_ROUNDED,
                    size=64,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(height=16),
                ft.Text(
                    "No internet access",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                ft.Text(
                    "Waiting for connection...",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.ProgressRing(width=24, height=24, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=40,
    )
