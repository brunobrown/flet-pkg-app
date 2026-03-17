import flet as ft

from src.presentation.themes.colors import DARK_ACCENT


@ft.component
def LoadingIndicator(message: str = "Loading...") -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(color=DARK_ACCENT),
                ft.Text(message, size=14, color="#9e9e9e"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        alignment=ft.Alignment.CENTER,
        padding=40,
    )


@ft.component
def ErrorMessage(message: str, on_retry: object = None) -> ft.Control:
    controls: list[ft.Control] = [
        ft.Icon(ft.Icons.ERROR_OUTLINE, size=40, color="#f44336"),
        ft.Text(message, size=14, color="#f44336", text_align=ft.TextAlign.CENTER),
    ]
    if on_retry:
        controls.append(
            ft.TextButton(
                "Retry",
                on_click=lambda _: on_retry(),
                style=ft.ButtonStyle(color=DARK_ACCENT),
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment.CENTER,
        padding=40,
    )
